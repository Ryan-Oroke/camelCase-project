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

import unittest
import random

from math import radians, cos, sin, asin, sqrt

#from haversine import haversine, Unit

UPLOAD_DIRECTORY = 'upload_files'  # I really don't like this, this is a flask thing not a mongo thing

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


#from https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def haversine(lat1, lon1, lat2, lon2):
    R = 3959.87433  # this is in miles.  For Earth radius in kilometers use 6372.8 km

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))

    return R * c

def getLatRange(desired_dist, curr_lat, curr_lon):
    #Pseudo Code

    #1. Convert the lat and lon to their int value
    #2. Using these two, get the distance between lat and lat+1
    #3. Interpolate the dist with lat/lon dist to coords change
    #4. Return max displacement range
    
    curr_lat = int(abs(curr_lat))
    curr_lon = int(abs(curr_lon))

    step = 0.01 #I have used 0.01 as the interpolation element, which is ~1km at 40N

    shifted_lat = curr_lat + step 

    curr_loc = (curr_lat, curr_lon)
    shifted_loc = (shifted_lat, curr_lon)

    #Get distance bewteen curr and shited location
    #coords_dist = haversine(curr_loc, shifted_loc, unit=Unit.MILES)*5280
    coords_dist = haversine(curr_lat, curr_lon, shifted_lat, curr_lon)*5280;

    range_lat = desired_dist/coords_dist * step

    return range_lat

def getLonRange(desired_dist, curr_lat, curr_lon):
    #Pseudo Code

    #1. Convert the lat and lon to their int value
    #2. Using these two, get the distance between lat and lat+1
    #3. Interpolate the dist with lat/lon dist to coords change
    #4. Return max displacement range
    
    curr_lat = int(abs(curr_lat))
    curr_lon = int(abs(curr_lon))

    step = 0.01 #I have used 0.01 as the interpolation element, which is ~1km at 40N

    shifted_lon = curr_lon + step 

    curr_loc = (curr_lat, curr_lon)
    shifted_loc = (curr_lat, shifted_lon)

    #Get distance bewteen curr and shited location
    #coords_dist = haversine(curr_loc, shifted_loc, unit=Unit.MILES)*5280
    coords_dist = haversine(curr_lat, curr_lon, curr_lat, shifted_lon)*5280

    range_lon = desired_dist/coords_dist * step

    return range_lon

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
        return self.connected

    def ins_file(self, entry):
        bson_data = entry._asdict()
        x = self.coll_file.insert_one(bson_data)
        return x

    def __remove_end_of_life(self, file_list):
        now = time.time()
        end_of_life_files = [f for f in file_list if f['file_create_time'] + f['vis_time'] < now and f['vis_time'] != -1]
        live_files = [f for f in file_list if f['file_create_time'] + f['vis_time'] >= now or f['vis_time'] == -1]

        test = [{'_id': file['_id']} for file in end_of_life_files]
        for file in end_of_life_files:
            self.coll_file.delete_one({"_id": file['_id']})
            try:
                file_path = os.path.join('static', UPLOAD_DIRECTORY, file['file_path'])
                print(file_path)
                os.remove(file_path)
                # I think we would use a call back to do this: thats to much work
            except:
                pass  # if we fail don't worry about it

        return live_files

    def __remove_out_of_range(self, file_list, lat, lon):
        file_lat_range = 0
        file_lon_range = 0
        new_list = []
        for f in file_list:
            #Radius on the file
            gps_lat_radius = getLatRange(f['vis_dist'], lat, lon)
            gps_lon_radius = getLonRange(f['vis_dist'], lat, lon)

            file_lat = f['gps_lat']
            file_lon = f['gps_long']

            lat_min = file_lat - gps_lat_radius
            lat_max = file_lat + gps_lat_radius
            lon_min = file_lon - gps_lon_radius
            lon_max = file_lon + gps_lon_radius

            #haversineDistFt = haversine((f['gps_lat'], f['gps_long']), (lat, lon), unit=Unit.MILES)
            haversineDistFt = haversine(f['gps_lat'], f['gps_long'], lat, lon)*5280

            if( lat > lat_min and lat < lat_max and lon > lon_min and lon < lon_max):
                new_list.append(f)
                print("IN RANGE: " + f['file_name'] + "(Visible: " + str(f['vis_dist'])+ "ft.) Location: (" + str(f['gps_lat']) + ", " + str(f['gps_long']) + ")" + ", Actual Range: (" + str(haversineDistFt) + "mi.) Range: (" + str(gps_lat_radius)  + str(gps_lon_radius) + ", " + str(haversine(lat, lon, (lat + gps_lat_radius), (lon + gps_lon_radius))) + "mi.) User Location: (" + str(lat) + ", " + str(lon) + ")")
            else:
                print("REMOVED: " + f['file_name'] + "(Visible: " + str(f['vis_dist'])+ "ft.) Location: (" + str(f['gps_lat']) + ", " + str(f['gps_long']) + ") Range: (" + str(gps_lat_radius) + ", " + str(gps_lon_radius) + ") User Location: (" + str(lat) + ", " + str(lon) + ")")



        return new_list;

    def get_all_files_for_user(self, username, max_files):
        cursor = self.coll_file.find({"creator_name": {"$eq": username}}).limit(max_files)
        file_list = list(cursor)
        file_list = self.__remove_end_of_life(file_list)
        return file_list

    def get_all_files_in_range(self, lat, long, gps_lat_radius, gps_lon_radius, max_files):
        lat_min = lat - gps_lat_radius
        lat_max = lat + gps_lat_radius
        long_min = long - gps_lon_radius
        long_max = long + gps_lon_radius
        cursor = self.coll_file.find({"gps_lat": {"$gte": lat_min, "$lte": lat_max}, "gps_long": {"$gte": long_min, "$lte": long_max}}).limit(max_files)
        file_list = list(cursor)
        file_list = self.__remove_end_of_life(file_list)
        file_list = self.__remove_out_of_range(file_list, lat, long)
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


class MyTest(unittest.TestCase):
    def test_can_connect_to_localhost(self):
        db_info_test = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
        self.assertEqual(db_info_test.connect(), True)

    def test_can_ins_file(self):
        db_info_test = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
        db_info_test.connect()

        res = db_info_test.ins_file(
            file_data_entry("test_user0", "test1", "abc", time.time(), "test_user0/P1540913.JPG", False, "", 40.015869,
                            -105.279517, 10, 1.0, 69, 1))

        self.assertIsNotNone(res)  # should return _id

    def test_can_find_file(self):
        db_info_test = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
        db_info_test.connect()

        db_info_test.ins_file(
            file_data_entry("test_user1", "test1", "abc", time.time(), "test_user1/P1540913.JPG", False, "", 40.015869,
                            -105.279517, 10, -1.0, 69, 1))  # -1 is inf time
        db_info_test.ins_file(
            file_data_entry("test_user1", "test2", "def", time.time(), "test_user1/P1540506.JPG", False, "", 40.016869,
                            -105.278617, 10, 2.0, 420, 2))
        db_info_test.ins_file(
            file_data_entry("test_user2", "test3", "111", time.time(), "test_user2/P1540915.JPG", False, "", 40.017869,
                            -105.275517, 10, 2.0, 10, 3))
        db_info_test.ins_file(
            file_data_entry("test_user2", "test4", "222", time.time(), "test_user2/test_pdf.pdf", False, "", 40.014869,
                            -105.276617, 10, 2.0, 20, 4))
        db_info_test.ins_file(
            file_data_entry("test_user3", "test5", "333", time.time(), "test_user3/LkgdAgN.jpg", False, "", 40.013869,
                            -105.277617, 10, 2.0, 30, 5))
        time.sleep(.1)

        data = db_info_test.get_all_files_in_range(40.015869, -105.279517, 2, 6)

        self.assertNotEqual(len(data), 0)

        data = db_info_test.get_all_searchable_files(40.015869, -105.279517, 2, 6, "test[0-9]")

        self.assertNotEqual(len(data), 0)

        data = db_info_test.get_all_files_for_user("test_user3", 6)

        self.assertNotEqual(len(data), 0)

    def test_can_create_user(self):
        db_info_test = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
        db_info_test.connect()

        name = "test_" + str(random.randint(0, 1000000))
        x = db_info_test.try_create_user(name, "password", "te", "st", name+"@b.c", "bio")

        self.assertIsNotNone(x)

        x = db_info_test.try_create_user(name, "password", "te", "st", name+"hreerasdasd@b.c", "bio")
        self.assertIsNone(x)

        x = db_info_test.try_create_user(name+"sdfasdfasdfsd", "password", "te", "st", name+"@b.c", "bio")
        self.assertIsNone(x)

    def test_login_user(self):
        db_info_test = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
        db_info_test.connect()

        name = "test_" + str(random.randint(0, 1000000))
        x = db_info_test.try_create_user(name, "password", "te", "st", name+"@b.c", "bio")

        self.assertIsNotNone(x)
        x = db_info_test.try_get_user(name, "password")
        self.assertIsNotNone(x)
        x = db_info_test.try_get_user(name+"@b.c", "password")
        self.assertIsNotNone(x)

    def test_login_user_fail(self):
        db_info_test = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
        db_info_test.connect()

        name = "test_" + str(random.randint(0, 1000000))
        x = db_info_test.try_create_user(name, "password", "te", "st", name+"@b.c", "bio")

        self.assertIsNotNone(x)
        x = db_info_test.try_get_user(name, "wrong_password")
        self.assertIsNone(x)


if __name__ == "__main__":
    unittest.main()

