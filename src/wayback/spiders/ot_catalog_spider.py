from scrapy import Spider, Selector, Request
from scrapy.http import Response

from wayback.items import TimeItem


class OTSpiderTime(Spider):
    name = 'wayback_time'
    allowed_domains = ['web.archive.org']

    base_url = 'http://web.archive.org'
    start_urls = [
        # 'http://web.archive.org/web/20090904201625/http://www.opentable.com/new-york-restaurant-listings?',
        'http://web.archive.org/web/20140122110428/http://www.opentable.com/new-york-restaurant-listings',
    ]

    def __init__(self, name=None, **kwargs):
        super(OTSpiderTime, self).__init__(name=None, **kwargs)
        self.limit = 0
        self.processed = 0

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




        # self.logger.info("Total to process: " + str(len(data_rows)))
        #
        # for row in data_rows:
        #
        #     if self.limit == self.settings.get('LIMIT'):
        #         return
        #
        #     item = WaybackItem()
        #     item['name'] = row.xpath('.//a[@class="r"]/text()').extract_first()
        #     [item['neighborhood'], item['type']] = row.xpath('.//div[@class="d"]/text()').extract_first().split("|")
        #
        #     stars_count = row.xpath('.//div[@class="Ratings"]/div/@title').extract_first()
        #     item['stars'] = [float(s) for s in stars_count.split() if is_float(s)][0] if stars_count else "-1"
        #
        #     item['reviews'] = row.xpath('.//span[@class="reviews"]/preceding-sibling::text()').extract_first()
        #     item['price'] = str(len(row.xpath('.//td[@class="PrCol"]/text()').extract_first()))
        #     item['url'] = row.xpath('.//a[@class="r"]/@href').extract_first()
        #
        #     request = Request(self.base_url + str(item['url']), callback=self.parse_address)
        #
        #     request.meta['item'] = item
        #     yield request
        #     self.limit += 1

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
