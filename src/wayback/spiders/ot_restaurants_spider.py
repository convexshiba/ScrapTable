from urllib.parse import urljoin

import pymongo
from scrapy import Spider, Selector, Request
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from geo.googlemap import GoogleMap
from mongotable.mongo_dict import MongoDict, COLLECTION
from util.tool import is_float
from wayback.items import OTItem


class OTRestaurantsSpider(Spider):
    name = 'ot_restaurants_spider.py'
    allowed_domains = ['web.archive.org']

    base_url = 'http://web.archive.org/'

    def __init__(self, **kwargs):
        super(OTRestaurantsSpider, self).__init__(name=None, **kwargs)
        self.limit = 0
        self.processed = 0
        self.mongo = MongoDict()
        self.gm = GoogleMap()

    def start_requests(self):
        limit = self.settings.get('DO_FIRST') if self.settings.get('DO_FIRST') >= 1 else 9999999

        for entry in self.mongo.get_collection_iterator(COLLECTION.OT_CATALOG).sort('key', pymongo.ASCENDING).limit(limit):
            entry_dict = entry['value']
            request = Request(url=entry_dict['url'], callback=self.parse_restaurant_page)
            request.meta['ot_catalog_key'] = entry['key'] + "_" + entry['value']['entry_number']

            # if request.meta['ot_catalog_key'] in self.mongo.client[self.settings.get("OUTPUT_DB")].collection_names():
            #     self.logger.critical(entry['key'] + " skipped")
            #     continue

            # self.limit += 1
            # if self.limit >= self.settings.get('LIMIT_CATALOG'):
            #     return

            if entry['key'] != "20110720053652":
                self.logger.debug(entry['key'] + " skipped")
                continue
            self.logger.critical(entry['key'] + " REQUESTED")

            yield request

    def parse_restaurant_page(self, response: Response):
        self.logger.debug(response.meta['ot_catalog_key'] + " is received")
        for request in self.try_parse(response):
            yield request

    def try_parse(self, response: Response):
        selector = Selector(response)

        data_rows = selector.xpath('//tr[@class = "a" or @class = "r"]')

        if len(data_rows) == 0:
            data_rows = selector.xpath('//tr[contains(@class, "ResultRow")]')

        if len(data_rows) == 0:
            self.logger.error(response.url + " no data!")
            raise CloseSpider("data row is empty: " + response.url)

        self.logger.debug("Found: " + str(len(data_rows)))

        for row in data_rows:
            yield self.try_parse_row(row, response)

    def try_parse_row(self, row: Selector, response: Response):
        item = OTItem()

        item['ot_catalog_key'] = response.meta['ot_catalog_key']

        # extract name
        item['name'] = row.xpath('.//a[@href]/text()').extract_first()

        # extract neighborhood
        neighborhood = row.xpath('.//div[@class="nn"]/text()').extract_first()
        if neighborhood is not None:
            item['neighborhood'] = neighborhood.strip()

        if 'neighborhood' not in item:
            neighborhood = row.xpath('.//div[@class="d"]/text()').extract_first()
            if neighborhood is not None:
                item['neighborhood'] = neighborhood.strip().split("|")[0]

        # extract type
        type_r = row.xpath('.//div[@class="nf"]/text()').extract_first()
        if type_r is not None:
            item['type'] = type_r.strip()

        if 'type' not in item:
            type_r = row.xpath('.//div[@class="d"]/text()').extract_first()
            if type_r is not None:
                item['type'] = type_r.strip().split("|")[1]

        # extract price
        price = row.xpath('.//td[@class="p"]/text()').extract_first()
        if price is not None:
            item["price"] = len(price)

        if 'price' not in item:
            price = row.xpath('.//td[@class="PrCol"]/text()').extract_first()
            if price is not None:
                item["price"] = len(price)

        # extract url
        url = row.xpath('.//a[@class="r"]/@href').extract_first()
        if url is not None:
            item['url'] = urljoin(response.url, url)

        if 'url' not in item:
            url = row.xpath('.//a[@href]/@href').extract_first()
            if url is not None:
                item['url'] = urljoin(response.url, url)

        # extract stars
        stars = row.xpath('.//div[@class="Ratings"]/div/@title').extract_first()
        if stars is not None:
            item['stars'] = [float(s) for s in stars.split() if is_float(s)][0] if stars else "-1"
        else:
            item['stars'] = -1

        # extract reviews
        reviews = row.xpath('.//span[@class="reviews"]/preceding-sibling::text()').extract_first()
        if reviews is not None:
            item['reviews'] = int(reviews)
        else:
            item['reviews'] = -1

        #
        request = Request(item['url'], callback=self.extract_geo_fields, dont_filter=True, errback=self.err_yield_item)
        request.meta['item'] = item
        return request

    def err_yield_item(self, response: Response):
        item = response.meta['item']
        yield


    def extract_geo_fields(self, response: Response):
        item = response.meta['item']
        selector = Selector(response)

        try:
            address = selector.xpath('//li[@class="RestProfileAddressItem"]/text()').extract()
            # self.logger.error("(" + "".join(address) + ")")
            # self.logger.error(1)

            if len(address) == 0:
                address = selector.xpath('//span[@id="RestSearch_lblFullAddress"]/text()').extract()
                # self.logger.error("(" + "".join(address) + ")")
                # self.logger.error(2)

            if len(address) == 0:
                address = selector.xpath('//div[@class="RestProfileAddress"]/text()').extract()
                if len("".join(address).strip()) == 0:
                    address = ""
                # self.logger.error("(" + "".join(address) + ")")
                # self.logger.error(3)

            if len(address) == 0:
                address = selector.xpath('//span[@id="ProfileOverview_lblAddressText"]/text()').extract()
                # self.logger.error("(" + "".join(address) + ")")
                # self.logger.error(4)

            if len(address) == 0:
                address = selector.xpath('//span[@itemprop="streetAddress"]/text()').extract()
                # self.logger.error("(" + "".join(address) + ")")
                # self.logger.error(5)

            if len(address) != 0:
                address = ",".join([str(line).strip().replace('\"', '') for line in address])
                item['address'] = address

            if len(address) == 0:
                raise KeyError

                # cleanup address to remove things in bracket
            # eg: 714 Seventh Avenue (inside Renaissance Hotel)
            start = item['address'].find('(')
            end = item['address'].find(')')
            if start != -1 and end != -1:
                item['address'] = item['address'][:start - 1] + item['address'][end + 1:]

                # extract geocode
            item['geocode'] = self.gm.geocode(item['address'])

            if len(item['geocode']) == 0:
                self.logger.error("geocode empty: " + item['address'])
                raise KeyError

            item['geocode'] = item['geocode'][0]
            # extract county
            item['county'] = self.extract_county(item['geocode']['address_components'], item)

            # extract place_id
            item['place_id'] = item['geocode']['place_id']

            # set is_nyc
            item['is_nyc'] = self.gm.check_if_nyc(item['county'])

            item['extract_success'] = True
        except KeyError or IndexError:
            item['extract_success'] = False
            # self.logger.error("Extract failed. Saved anyway: " + str(item))

        yield item

    def verify(self, item: OTItem, field: str, response: Response):
        if field not in item or item[field] is None:
            raise CloseSpider("extract field failed: " + field + " " + response.url)
        else:
            self.logger.debug("Success: " + str(item[field]))
            pass

    def extract_county(self, geocode, item):
        for entry in geocode:
            if 'administrative_area_level_2' in entry['types']:
                return entry['long_name']
        self.logger.critical("County Not found: " + str(item))

