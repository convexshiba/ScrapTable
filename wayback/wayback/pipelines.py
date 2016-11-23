# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import tablib


class WaybackPipeline(object):
    def __init__(self):
        self.output = open('wayback.csv', 'w+')
        self.dataset = tablib.Dataset()

    def open_spider(self, spider):
        self.dataset.headers = ["name",
                                "neighborhood",
                                "type",
                                "stars",
                                "reviews",
                                "price",
                                "address",
                                "url"]

    def close_spider(self, spider):
        self.output.write(self.dataset.csv)
        self.output.close()

    def process_item(self, item, spider):
        self.add_item_to_dataset(item)
        return item

    def add_item_to_dataset(self, item):
        self.dataset.append(
            [str(item.get(field)).strip() for field in self.dataset.headers]
        )
