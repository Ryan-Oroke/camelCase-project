import pymongo
from typing import NamedTuple, MutableMapping
from dataclasses import dataclass
import collections
import bson
import uuid
import hashlib
import time
import os


class file_data_entry(NamedTuple):
    #user_created_name: int  # change to ObjectID or username

    file_name: str
    #file_description: str
    file_create_time: float  # secs from
    file_path: str
    #file_password: str

    gps_lat: float
    gps_long: float
    vis_dist: int
    vis_time: float  # secs

    #num_likes: int


class user_data_entry(NamedTuple):
    user_name: str  # plain text
    password_hash: str  # hashlib

    first_name: str
    last_name: str
    email: str


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
                os.remove(file['file_path'])
            except:
                pass

        return live_files

    def get_all_files_in_range(self, lat, long, gps_radius, max_files):
        lat_min = lat - gps_radius
        lat_max = lat + gps_radius
        long_min = long - gps_radius
        long_max = long + gps_radius
        cursor = self.coll_file.find({"gps_lat": {"$gte": lat_min, "$lte": lat_max}, "gps_long": {"$gte": long_min, "$lte": long_max}}).limit(max_files)
        file_list = list(cursor)
        file_list = self.__remove_end_of_life(file_list)
        return file_list

    def try_create_user(self, user_name, password_plain_text, first_name, last_name, email):
        password_hash = hashlib.sha256(password_plain_text.encode('utf-8')).hexdigest()
        user_info = user_data_entry(user_name, password_hash, first_name, last_name, email)
        bson_data = user_info._asdict()
        try:
            res = self.coll_user.insert_one(bson_data)
            return res.inserted_id
        except:
            return None

    def try_get_user(self, user_name, password_plain_text):
        password_hash = hashlib.sha256(password_plain_text.encode('utf-8')).hexdigest()
        x = self.coll_user.find_one({"user_name": user_name, "password_hash": password_hash})
        return x  # so if x is None then username or password is wrong


if __name__ == "__main__":
    db_info = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
    db_info.connect()

    db_info.ins_file(file_data_entry("test0", time.time(), "", 0, 0, 10, 2.0))
    db_info.ins_file(file_data_entry("test1", time.time(), "", 1, 1.5, 10, 2.0))
    db_info.ins_file(file_data_entry("test2", time.time(), "", 1.9, 0.8, 10, 0))
    db_info.ins_file(file_data_entry("test3", time.time(), "", 2.1, 0.1, 10, 0))
    db_info.ins_file(file_data_entry("test4", time.time(), "", 3.2, 3, 10, 2.0))
    db_info.ins_file(file_data_entry("test5", time.time(), "", 1.3, 2.1, 10, 0))

    time.sleep(1)

    data = db_info.get_all_files_in_range(0,0,2,6)

    print(data)

    # user stuff
    x = db_info.try_create_user("test1", "password", "te", "st", "a@b.c")
    print(x)
    x = db_info.try_get_user("test2", "password")
    print(x)

