from scrapy import *

from util.googlemap import GoogleMap
from util.tool import is_float
from wayback.items import WaybackItem


class OTSpider(Spider):
    name = 'wayback'
    allowed_domains = ['web.archive.org']

    base_url = 'http://web.archive.org/web/20111205224627/http://www.opentable.com/'
    start_urls = [
        'http://web.archive.org/web/20111205224627/http://www.opentable.com/new-york-restaurant-listings',
    ]

    def __init__(self, name=None, **kwargs):
        super(OTSpider, self).__init__(name=None, **kwargs)
        self.limit = 0
        self.processed = 0
        self.gm = GoogleMap()

    def parse(self, response):

        rows = Selector(response).xpath('//tr[contains(@class, "Result")]')

        self.logger.info("Total to process: " + str(len(rows)))

        for row in rows:

            if self.limit == self.settings.get('LIMIT'):
                return

            item = WaybackItem()
            item['name'] = row.xpath('.//a[@class="r"]/text()').extract_first()
            [item['neighborhood'], item['type']] = row.xpath('.//div[@class="d"]/text()').extract_first().split("|")

            stars_count = row.xpath('.//div[@class="Ratings"]/div/@title').extract_first()
            item['stars'] = [float(s) for s in stars_count.split() if is_float(s)][0] if stars_count else "-1"

            item['reviews'] = row.xpath('.//span[@class="reviews"]/preceding-sibling::text()').extract_first()
            item['price'] = str(len(row.xpath('.//td[@class="PrCol"]/text()').extract_first()))
            item['url'] = row.xpath('.//a[@class="r"]/@href').extract_first()

            request = Request(self.base_url + str(item['url']), callback=self.parse_address)

            request.meta['item'] = item
            yield request
            self.limit += 1

    def parse_address(self, response):
        item = response.meta['item']
        item['address'] = ','.join([str(line).strip().replace('\"', '') for line in
                                    response.selector.xpath('//span[@itemprop="streetAddress"]/text()').extract()])

        item['geocode'] = self.gm.geocode(item['address'])[0]['address_components']
        item['county'] = self.find_county(item['geocode'])
        item['is_nyc'] = self.gm.is_nyc(item['county'])

        self.processed += 1

        if self.limit % 50 == 0:
            self.logger.info("Processed: " + str(self.limit))

        yield item

    @staticmethod
    def find_county(geocode):
        for item in geocode:
            if 'administrative_area_level_2' in item['types']:
                return item['long_name']
