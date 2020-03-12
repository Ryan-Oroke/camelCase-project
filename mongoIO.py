import pymongo
from typing import NamedTuple, MutableMapping
from dataclasses import dataclass
import collections
import bson
import uuid
import hashlib


class file_data_entry(NamedTuple):
    #user_created_name: int  # change to uuid

    file_name: str
    #file_description: str
    #file_date: str
    #file_path: str
    #file_password: str

    #gps_lat: str
    #gps_log: str
    vis_dist: int
    #vis_time: int

    #num_likes: int


class user_data_entry(NamedTuple):
    user_name: str  # plain text
    password_hash: str  # hashlib

    #first_name: str
    #last_name: str
    #email: str


def to_file_data_entry(dict):
    dict.pop('_id')
    return file_data_entry(**dict)


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

        # collection.create_index([("user_name", ???)])

        self.connected = True

    def ins_file(self, entry):
        bson_data = entry._asdict()
        x = self.coll_file.insert_one(bson_data)

    def find(self, query_info):
        data = self.coll_file.find(query_info)
        return map(lambda d: to_file_data_entry(d), data)

    def create_user(self, user_name, password_plain_text):
        password_hash = hashlib.sha256(password_plain_text.encode('utf-8')).hexdigest()
        user_info = user_data_entry(user_name, password_hash)
        bson_data = user_info._asdict()
        x = self.coll_user.insert_one(bson_data)
        return x

    def get_user(self, user_name, password_plain_text):
        password_hash = hashlib.sha256(password_plain_text.encode('utf-8')).hexdigest()
        x = self.coll_user.find_one({"user_name": user_name, "password_hash": password_hash})
        return x


if __name__ == "__main__":
    db_info = DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")
    db_info.connect()

    for i in range(0,10):
        sample_data = file_data_entry("test" + str(i),i)  # ._asdict()
        x = db_info.ins_file(sample_data)

    data = db_info.find({"vis_dist": { "$gt": 7 }})

    print(x)
    print(data)
    print(list(data))

    # user stuff
    db_info.create_user("test", "password")
    x = db_info.get_user("test", "password")
    print(x)

