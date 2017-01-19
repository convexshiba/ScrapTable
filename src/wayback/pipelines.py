# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from logging import getLogger

from geo.googlemap import GoogleMap
from mongotable.mongo_dict import MongoDict, COLLECTION, OTRestPipelineMongo
from wayback.items import OTItem, TimeItem


class WaybackPipeline(object):
    def __init__(self):
        self.mongo_dict = MongoDict()
        self.gm = GoogleMap()

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item: OTItem, spider):
        self.add_item_to_db(item)
        return item

    def add_item_to_db(self, item: OTItem) -> None:
        pass


class WaybackTimePipeline(object):
    def __init__(self):
        self.mongo_dict = MongoDict()

    def process_item(self, item: TimeItem, spider):
        self.spider = spider
        self.add_item_to_db(item)
        return item

    def add_item_to_db(self, item: TimeItem) -> None:
        # self.mongo_dict.insert_item(COLLECTION.TEST, item)
        if [COLLECTION.OT_CATALOG, item['version_datetime']] not in self.mongo_dict:
            self.spider.logger.debug(item['version_datetime'] + " stored to DB")
            self.mongo_dict.put(COLLECTION.OT_CATALOG, item['version_datetime'], dict(item))
        else:
            self.spider.logger.debug(item['version_datetime'] + " exist. Skipped")
        pass


class OTRestaurantPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def __init__(self, settings):
        self.settings = settings
        self.logger = getLogger("OTRestaurantPipeline")
        self.mongo = OTRestPipelineMongo(self.settings.get("OUTPUT_DB"))

    def process_item(self, item: OTItem, spider):
        self.spider = spider
        self.mongo.store_otitem(item)
        return item
