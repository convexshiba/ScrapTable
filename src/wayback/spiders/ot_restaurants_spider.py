from urllib.parse import urljoin

from scrapy import Spider, Selector, Request
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

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

    def start_requests(self):
        for entry in self.mongo.get_collection_iterator(COLLECTION.OT_CATALOG):
            entry_dict = entry['value']
            request = Request(url=entry_dict['url'], callback=self.parse_restaurant_page)
            request.meta['ot_catalog_key'] = entry['key']

            self.limit += 1

            if self.limit == self.settings.get('LIMIT'):
                return

            yield request

    def parse_restaurant_page(self, response: Response):
        self.logger.debug(response.meta['ot_catalog_key'] + " is received")
        for request in self.try_parse(response):
            yield request
        self.logger.critical("processed: " + str(self.limit))

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

        request = Request(item['url'], callback=self.extract_address)
        request.meta['item'] = item
        return request

    def extract_address(self, response: Response):
        item = response.meta['item']
        selector = Selector(response)

        address = selector.xpath('//li[@class="RestProfileAddressItem"]/text()').extract()
        if len(address) == 0:
            address = selector.xpath('//span[@id="RestSearch_lblFullAddress"]/text()').extract()
        if len(address) == 0:
            address = selector.xpath('//div[@class="RestProfileAddress"]/text()').extract()
        if len(address) == 0:
            address = selector.xpath('//span[@id="ProfileOverview_lblAddressText"]/text()').extract()

        if len(address) == 0:
            self.logger.critical(address)
            self.logger.critical(len(address))
            self.logger.critical(response.url)

        if len(address) != 0:
            address = ",".join([str(line).strip().replace('\"', '') for line in address])
            item['address'] = address

        # if 'address' not in item:
        #     address = ','.join([str(line).strip().replace('\"', '') for line in
        #                         selector.xpath('//span[@itemprop="streetAddress"]/text()').extract()])
        #     if address is not "":
        #         item['address'] = address
        # self.verify(item, 'address', response)

    def verify(self, item: OTItem, field: str, response: Response):
        if field not in item or item[field] is None:
            raise CloseSpider("extract field failed: " + field + " " + response.url)
        else:
            self.logger.debug("Success: " + str(item[field]))
            pass


