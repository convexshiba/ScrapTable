from scrapy import Spider, Selector, Request
from scrapy.http import Response

from mongotable.mongo_dict import MongoDict, COLLECTION
from wayback.items import TimeItem


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
        self.logger.debug(response.meta['ot_catalog_key'] + " is crawled")

    def parse(self, response: Response):

        selector = Selector(response)
        data_rows = selector.xpath('//tr[@class = "a" or @class = "r"]').extract()

        if len(data_rows) == 0:
            data_rows = selector.xpath('//tr[contains(@class, "ResultRow")]').extract()

        if len(data_rows) == 0:
            self.logger.error(response.url + " no data!")

        item = TimeItem()
        item["url"] = response.url
        item['entry_number'] = str(len(data_rows))

        version_time_raw = selector.xpath('//td[contains(@id, "displayDayEl")]/@title').extract_first()
        item['version_datetime_string'] = version_time_raw[version_time_raw.find(':') + 2:]
        item['version_datetime'] = item["url"].split('/')[4]

        yield item

        next_button_url = selector.xpath('//img[contains(@alt, "Next capture")]/../@href').extract_first()

        if self.limit == self.settings.get('LIMIT'):
            return

        request = Request(self.base_url + next_button_url, callback=self.parse)
        request.meta['item'] = item
        yield request
        self.limit += 1

    def parse_address(self, response):
        item = response.meta['item']
        item['address'] = ','.join([str(line).strip().replace('\"', '') for line in
                                    response.selector.xpath('//span[@itemprop="streetAddress"]/text()').extract()])

        # item['geocode'] = self.gm.geocode(item['address'])[0]['address_components']
        # item['county'] = self.find_county(item['geocode'])
        # item['is_nyc'] = self.gm.is_nyc(item['county'])

        self.processed += 1

        if self.limit % 50 == 0:
            self.logger.info("Processed: " + str(self.limit))

        yield item
