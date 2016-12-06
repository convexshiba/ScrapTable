# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import *


class WaybackItem(Item):
    name = Field()
    neighborhood = Field()
    type = Field()
    stars = Field()
    reviews = Field()
    price = Field()
    url = Field()
    address = Field()
    geocode = Field()
    county = Field()
    is_nyc = Field()
