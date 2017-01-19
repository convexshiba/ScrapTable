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
    GEO_CACHE = 'geo_cache'
    TEST = 'test'
    DOH_RAW = 'doh_raw'


class MongoDict:
    def __init__(self) -> None:
        self.logger = getLogger("MongoHandler")
        self.logger.debug("Connecting to MongoDB")
        self.client = MongoClient("hungry.asuscomm.com", 27017)
        self.db = self.client["db"]

        self.doh_collection = self.db[COLLECTION.DOH.value]
        self.doh_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

        self.ot_collection = self.db[COLLECTION.OT.value]
        self.ot_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

        self.ot_catalog_collection = self.db[COLLECTION.OT_CATALOG.value]
        self.ot_catalog_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

        self.geo_cache_collection = self.db[COLLECTION.GEO_CACHE.value]
        self.geo_cache_collection.create_index([('key', pymongo.ASCENDING)], unique=True)

        self.test_collection = self.db[COLLECTION.TEST.value]

    def __contains__(self, item):
        [collection, key] = item
        self.verify_collection(collection)
        return self.db[collection.value].find({'key': key}).count() != 0

        # if collection == COLLECTION.DOH:
        #     return self.doh_collection.find({'key': key}).count() != 0
        # if collection == COLLECTION.OT:
        #     return self.ot_collection.find({'key': key}).count() != 0
        # if collection == COLLECTION.OT_CATALOG:
        #     return self.ot_catalog_collection.find({'key': key}).count() != 0
        # raise Exception("Invalid database")

    def put(self, collection: COLLECTION, key, value):
        self.verify_collection(collection)
        self.db[collection.value].update({'key': key}, to_dict(key, value), upsert=True)

        # if collection == COLLECTION.DOH:
        #     self.doh_collection.update({'key': key}, to_dict(key, value), upsert=True)
        #     return
        # if collection == COLLECTION.OT:
        #     self.ot_collection.update({'key': key}, to_dict(key, value), upsert=True)
        #     return
        # if collection == COLLECTION.OT_CATALOG:
        #     self.ot_catalog_collection.update({'key': key}, to_dict(key, value), upsert=True)
        #     return
        # raise Exception("Invalid database")

    def get(self, collection: COLLECTION, key):
        self.verify_collection(collection)
        if [collection, key] in self:
            return self.db[collection.value].find({'key': key})[0]['value']

    def insert_item(self, collection, item: Item):
        if collection == COLLECTION.TEST:
            self.test_collection.insert(dict(item))
            return
        raise Exception("Invalid database")

    def get_collection_iterator(self, collection: COLLECTION):
        self.verify_collection(collection)
        return self.db[collection.value].find({})
        # if collection == COLLECTION.DOH:
        #     return self.doh_collection.find({})
        # if collection == COLLECTION.OT:
        #     return self.ot_collection.find({})
        # if collection == COLLECTION.OT_CATALOG:
        #     return self.ot_catalog_collection.find({})

    def verify_collection(self, collection: COLLECTION):
        if collection not in COLLECTION:
            raise Exception("Invalid database")


class OTRestPipelineMongo(MongoDict):
    def __init__(self, output_db: str):
        MongoDict.__init__(self)
        self.ot_db = self.client[output_db]
        self.logger = getLogger("OTRestPipelineMongo")

        self.set = {}

    def store_otitem(self, item):
        collection = item['ot_catalog_key']
        if item['extract_success']:
            item_key_base = item['place_id']
        else:
            item_key_base = item['name']

        item_key = item_key_base
        tie = 1
        while item_key in self.set:
            item_key = item_key_base + "_" + str(tie)
            tie += 1

        value = item
        key_collection = self.init_collection(collection)
        key_collection.update({'key': item_key}, to_dict(item_key, value), upsert=True)
        self.set[item_key] = True

        # if item_key not in self.set:
        #     self.set[item_key] = item
        # else:
        #     self.logger.error("FOUND DUPLICATE item_key: " + item_key)
        #     if item_key in self.dub:
        #         self.dub[item_key].append(item)
        #     else:
        #         self.dub[item_key] = [self.set[item_key], item]
        #     self.logger.error(self.dub[item_key])

    def init_collection(self, key):
        collection = self.ot_db[key]
        collection.create_index([('key', pymongo.ASCENDING)], unique=True)
        return collection

