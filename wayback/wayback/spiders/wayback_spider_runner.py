from scrapy.crawler import CrawlerProcess

from wayback.spiders.wayback_spider import OTSpider

# configure_logging(install_root_handler=False)
# logging.basicConfig(level=logging.INFO)

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'LOG_LEVEL': 'DEBUG',
    'ITEM_PIPELINES': {
        'wayback.pipelines.WaybackPipeline': 10,
    },
    'LIMIT': 200,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 2,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 3.5,
})

process.crawl(OTSpider)
process.start()  # the script will block here until the crawling is finished
