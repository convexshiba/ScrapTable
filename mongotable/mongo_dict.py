from enum import Enum
from logging import getLogger

import pymongo
from pymongo import MongoClient


class DummyClass: pass


def to_dict(key, value):
    return {
        'key': key,
        'value': value,
    }


class DB(Enum):
    DOH = 'doh_geo'
    OT = 'ot_geo'
    TEST = 'test'


class MongoDict:
    def __init__(self):
        self.logger = getLogger("MongoHandler")
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["db"]
        self.doh_collection = self.db[DB.DOH.value]
        self.doh_collection.create_index([('key', pymongo.ASCENDING)], unique=True)
        self.ot_collection = self.db[DB.OT.value]
        self.ot_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

    def __contains__(self, item):
        [collection, key] = item
        if collection == DB.DOH:
            return self.doh_collection.find({'key': key}).count() != 0
        if collection == DB.OT:
            return self.ot_collection.find({'key': key}).count() != 0
        raise Exception("Invalid database")

    def put(self, collection, key, value):
        if collection == DB.DOH:
            self.doh_collection.update({'key': key}, to_dict(key, value), upsert=True)
            return
        if collection == DB.OT:
            self.ot_collection.update({'key': key}, to_dict(key, value), upsert=True)
            return
        raise Exception("Invalid database")
