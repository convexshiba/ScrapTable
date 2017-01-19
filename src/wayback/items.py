# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import *


class OTItem(Item):
    # done
    name = Field()
    neighborhood = Field()
    type = Field()
    stars = Field()
    reviews = Field()
    price = Field()
    url = Field()
    address = Field()
    geocode = Field()
    ot_catalog_key = Field()
    county = Field()
    is_nyc = Field()
    place_id = Field()
    extract_success = Field()


class TimeItem(Item):
    entry_number = Field()
    url = Field()
    version_datetime_string = Field()
    version_datetime = Field()
