from scrapy import *

from wayback.items import WaybackItem
from wayback.spiders.util import *


class OTSpider(Spider):
    name = 'wayback'
    allowed_domains = ['web.archive.org']

    base_url = 'http://web.archive.org/web/20111205224627/http://www.opentable.com/'
    start_urls = [
        'http://web.archive.org/web/20111205224627/http://www.opentable.com/new-york-restaurant-listings',
    ]

    def __init__(self, name=None, **kwargs):
        super(OTSpider, self).__init__(name=None, **kwargs)
        self.processed = 0

    def parse(self, response):

        rows = Selector(response).xpath('//tr[contains(@class, "Result")]')

        self.logger.info("Total to process: " + str(len(rows)))

        limit = 0

        for row in rows:

            if limit == self.settings.get('LIMIT'):
                return

            item = WaybackItem()
            item['name'] = row.xpath('.//a[@class="r"]/text()').extract_first()
            [item['neighborhood'], item['type']] = row.xpath('.//div[@class="d"]/text()').extract_first().split("|")

            starsCnt = row.xpath('.//div[@class="Ratings"]/div/@title').extract_first()
            item['stars'] = [float(s) for s in starsCnt.split() if isFloat(s)][0] if starsCnt else "-1"

            item['reviews'] = row.xpath('.//span[@class="reviews"]/preceding-sibling::text()').extract_first()
            item['price'] = str(len(row.xpath('.//td[@class="PrCol"]/text()').extract_first()))
            item['url'] = row.xpath('.//a[@class="r"]/@href').extract_first()

            request = Request(self.base_url + str(item['url']), callback=self.parse_address)

            request.meta['item'] = item
            yield request
            limit += 1

    def parse_address(self, response):
        item = response.meta['item']
        item['address'] = '-'.join([str(line).strip().replace('\"', '').replace(',', "-") for line in
                                    response.selector.xpath('//span[@itemprop="streetAddress"]/text()').extract()])

        self.processed += 1

        if self.processed % 100 == 0:
            self.logger.info("Processed " + str(self.processed))

        yield item
