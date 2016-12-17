from scrapy import Spider, Selector, Request
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from mongotable.mongo_dict import MongoDict, COLLECTION
from wayback.items import OTItem


class OTRestaurantsSpider(Spider):
    name = 'ot_restaurants_spider.py'
    allowed_domains = ['web.archive.org']

    base_url = 'http://web.archive.org'

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
            yield request

    def parse_restaurant_page(self, response: Response):
        self.logger.debug(response.meta['ot_catalog_key'] + " is received")
        self.try_parse(response)

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
            self.try_parse_row(row, response)

    def try_parse_row(self, row: Selector, response: Response):
        item = OTItem()

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

    def verify(self, item: OTItem, field: str, response: Response):
        if field not in item or item[field] is None:
            raise CloseSpider("extract field failed: " + field + " " + response.url)
        else:
            self.logger.debug("Success: " + str(item[field]))
            pass


