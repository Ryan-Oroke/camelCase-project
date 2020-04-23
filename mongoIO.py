import pymongo
from typing import NamedTuple, MutableMapping
from dataclasses import dataclass
import collections
import bson
import uuid
import hashlib
import time
import os

from bson import ObjectId


class file_data_entry(NamedTuple):
    creator_name: str  # change to ObjectID or username

    file_name: str
    file_description: str
    file_create_time: float  # secs from
    file_path: str
    file_req_password: bool
    file_password_hash: str

    gps_lat: float
    gps_long: float
    vis_dist: float
    vis_time: float  # secs

    num_likes: int
    num_downloads: int


class user_data_entry(NamedTuple):
    user_name: str  # plain text
    password_hash: str  # hashlib

    first_name: str
    last_name: str
    email: str
    bio: str


"""
class file_data_entry(MutableMapping):
    def __init__(self, name, test):
        self.name = name
        self.test = test
"""


class DB_info:
    def __init__(self, host_server, host_port, db_name, file_coll_name, user_coll_name):
        self.host_server = host_server
        self.host_port = host_port
        self.db_name = db_name

        self.file_coll_name = file_coll_name
        self.user_coll_name = user_coll_name

        self.client = None
        self.db = None
        self.coll_file = None
        self.coll_user = None

        self.connected = False

    def connect(self):
        self.client = pymongo.MongoClient(self.host_server, self.host_port)

        self.db = self.client[self.db_name]

        self.coll_file = self.db[self.file_coll_name]
        self.coll_user = self.db[self.user_coll_name]

        self.coll_file.create_index([("gps_lat", pymongo.DESCENDING), ("gps_long", pymongo.ASCENDING)])

        self.coll_user.create_index("user_name", unique=True, dropDups=1)
        self.coll_user.create_index("email", unique=True, dropDups=1)

        self.connected = True

    def ins_file(self, entry):
        bson_data = entry._asdict()
        x = self.coll_file.insert_one(bson_data)

    def __remove_end_of_life(self, file_list):
        now = time.time()
        end_of_life_files = [f for f in file_list if f['file_create_time'] + f['vis_time'] < now]
        live_files = [f for f in file_list if f['file_create_time'] + f['vis_time'] >= now]

        test = [{'_id': file['_id']} for file in end_of_life_files]
        for file in end_of_life_files:
            self.coll_file.delete_one({"_id": file['_id']})
            try:
                pass  # os.remove(file['file_path'])
                # I think we would use a call back to do this
            except:
                pass

        return live_files

    def get_all_files_for_user(self, username, max_files):
        cursor = self.coll_file.find({"creator_name": {"$eq": username}}).limit(max_files)
        file_list = list(cursor)
        file_list = self.__remove_end_of_life(file_list)
        return file_list

    def get_all_files_in_range(self, lat, long, gps_radius, max_files):
        lat_min = lat - gps_radius
        lat_max = lat + gps_radius
        long_min = long - gps_radius
        long_max = long + gps_radius
        cursor = self.coll_file.find({"gps_lat": {"$gte": lat_min, "$lte": lat_max}, "gps_long": {"$gte": long_min, "$lte": long_max}}).limit(max_files)
        file_list = list(cursor)
        file_list = self.__remove_end_of_life(file_list)
        return file_list

    def update_user_bio(self, user, bio):
        self.coll_user.update({'user_name': user}, {'$set': {'bio': bio}})
        print(self.coll_user.find({"user_name": user}))

    def get_user_bio(self, user):
        #print(list(self.coll_user.find({"user_name": user}, {"bio": 1})))
        return list(self.coll_user.find({"user_name": user}, {"bio": 1}))
        #return self.coll_user.find({"user_name": user}, {"bio": 1})

    def update_file_downloads(self, id):
        self.coll_file.update_one({'_id': ObjectId(id)}, {'$inc': {'num_downloads': 1}})
        

    def get_all_searchable_files(self, lat, long, gps_radius, max_files, searc):
        lat_min = lat - gps_radius
        lat_max = lat + gps_radius
        long_min = long - gps_radius
        long_max = long + gps_radius
        search_str = searc
        search_key = ''
        try:
            if search_str == '':
                cursor = self.coll_file.find({"gps_lat": {"$gte": lat_min, "$lte": lat_max}, "gps_long": {"$gte": long_min, "$lte": long_max}}).limit(max_files)
                file_list = list(cursor)
                file_list = self.__remove_end_of_life(file_list)
                return file_list
            else:
                if search_str[0] == '@':
                    #Search By User
                    search_list = list(search_str)
                    #print(search_list)
                    search_list.remove('@')
                    search_str = search_key.join(search_list)
                    #print(search_str)
                    cursor = self.coll_file.find({"creator_name": { "$regex" : search_str}, "gps_lat": {"$gte": lat_min, "$lte": lat_max}, "gps_long": {"$gte": long_min, "$lte": long_max}}).limit(max_files)
                else:
                    cursor = self.coll_file.find({"file_name": { "$regex" : search_str}, "gps_lat": {"$gte": lat_min, "$lte": lat_max}, "gps_long": {"$gte": long_min, "$lte": long_max}}).limit(max_files)
                file_list = list(cursor)
                file_list = self.__remove_end_of_life(file_list)
                return file_list;
        except:
                return []

    def try_create_user(self, user_name, password_plain_text, first_name, last_name, email, bio):
        password_hash = hashlib.sha256(password_plain_text.encode('utf-8')).hexdigest()
        user_info = user_data_entry(user_name, password_hash, first_name, last_name, email, bio)
        bson_data = user_info._asdict()
        try:
            res = self.coll_user.insert_one(bson_data)
            return res.inserted_id
        except:
            return None

    def try_get_user(self, user_name_or_email, password_plain_text):
        password_hash = hashlib.sha256(password_plain_text.encode('utf-8')).hexdigest()
        x = self.coll_user.find_one({"user_name": user_name_or_email, "password_hash": password_hash})
        if x is None:
            x = self.coll_user.find_one({"email": user_name_or_email, "password_hash": password_hash})
            #print(x)
        return x  # so if x is None then username or password is wrong


if __name__ == "__main__":
    db_info = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
    db_info.connect()

    if False:
        db_info.ins_file(
            file_data_entry("test_user", "test1", "abc", time.time(), "test_user/P1540913.JPG", False, "", 40.015869,
                            -105.279517, 10, 100000.0, 69, 1))
        db_info.ins_file(
            file_data_entry("test_user", "test2", "def", time.time(), "test_user/P1540506.JPG", False, "", 40.016869,
                            -105.278617, 10, 100000.0, 420, 2))
        db_info.ins_file(
            file_data_entry("test_user", "test3", "111", time.time(), "test_user/P1540915.JPG", False, "", 40.017869,
                            -105.275517, 10, 200000.0, 10, 3))
        db_info.ins_file(
            file_data_entry("test_user", "test4", "222", time.time(), "test_user/test_pdf.pdf", False, "", 40.014869,
                            -105.276617, 10, 300000.0, 20, 4))
        db_info.ins_file(
            file_data_entry("test_user", "test5", "333", time.time(), "test_user/LkgdAgN.jpg", False, "", 40.013869,
                            -105.277617, 10, 100000.0, 30, 5))

    time.sleep(1)

    data = db_info.get_all_files_in_range(40.015869,-105.279517,2,6)

    print(data)

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0]['file_create_time'])))
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((data[0]['file_create_time'] + data[0]['vis_time']))))

    # user stuff
    x = db_info.try_create_user("test1", "password", "te", "st", "a@b.c")
    print(x)
    x = db_info.try_get_user("test1", "password")
    print(x)

    print(db_info.get_all_files_for_user('test_user', 10))

