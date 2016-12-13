from enum import Enum
from logging import getLogger

import pymongo
from pymongo import MongoClient
from scrapy import Item


class DummyClass: pass


def to_dict(key, value):
    return {
        'key': key,
        'value': value,
    }


class COLLECTION(Enum):
    DOH = 'doh_geo'
    OT = 'ot_geo'
    OT_CATALOG = 'ot_catalog'
    TEST = 'test'


class MongoDict:
    def __init__(self) -> None:
        self.logger = getLogger("MongoHandler")
        self.logger.debug("Connecting to MongoDB")
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["db"]

        self.doh_collection = self.db[COLLECTION.DOH.value]
        self.doh_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

        self.ot_collection = self.db[COLLECTION.OT.value]
        self.ot_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

        self.ot_catalog_collection = self.db[COLLECTION.OT_CATALOG.value]
        self.ot_catalog_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

        self.test_collection = self.db[COLLECTION.TEST.value]

    def __contains__(self, item):
        [collection, key] = item
        if collection == COLLECTION.DOH:
            return self.doh_collection.find({'key': key}).count() != 0
        if collection == COLLECTION.OT:
            return self.ot_collection.find({'key': key}).count() != 0
        if collection == COLLECTION.OT_CATALOG:
            return self.ot_catalog_collection.find({'key': key}).count() != 0
        raise Exception("Invalid database")

    def put(self, collection, key, value):
        if collection == COLLECTION.DOH:
            self.doh_collection.update({'key': key}, to_dict(key, value), upsert=True)
            return
        if collection == COLLECTION.OT:
            self.ot_collection.update({'key': key}, to_dict(key, value), upsert=True)
            return
        if collection == COLLECTION.OT_CATALOG:
            self.ot_catalog_collection.update({'key': key}, to_dict(key, value), upsert=True)
            return
        raise Exception("Invalid database")

    def insert_item(self, collection, item: Item):
        if collection == COLLECTION.DOH:
            self.logger.warning("Does not support item directly into doh database.\nUse put() instead.")
            return
        if collection == COLLECTION.OT:
            self.logger.warning("Does not support item directly into OT database.\nUse put() instead.")
            return
        if collection == COLLECTION.TEST:
            self.test_collection.insert(dict(item))
            return
        raise Exception("Invalid database")

    def get_collection_iterator(self, collection: COLLECTION):
        if collection == COLLECTION.DOH:
            return self.doh_collection.find({})
        if collection == COLLECTION.OT:
            return self.ot_collection.find({})
        if collection == COLLECTION.OT_CATALOG:
            return self.ot_catalog_collection.find({})
