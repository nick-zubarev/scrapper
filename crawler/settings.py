# -*- coding: utf-8 -*-
BOT_NAME = 'Bing'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Database configuration
DB_FILENAME = 'database.csv'
PRIMARY_FIELD = 'name'

# Compare and make unique with fuzzywuzzy
# token ration text processor
USE_MATCH_RATIO = False
MIN_MATCH_RATIO = 95 # in %

# May be disabled for some spiders
# ignoring this config
ENABLE_PROXY = True

# May cause errors
USE_FASTEST_PROXIES = True

# If you use fastest proxies, you can
# configure minimal speed in %
FASTEST_PROXIES_MINIMAL_SPEED = 70

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Used for filtering failed proxies
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 408]

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
   'scrapy.spidermiddlewares.offsite': None,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
   'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90 if ENABLE_PROXY else None,
   'crawler.utils.middleware.RandomProxy': 100 if ENABLE_PROXY else None,
   'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110 if ENABLE_PROXY else None,
   'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
}

# Configure item pipelines
ITEM_PIPELINES = {
   'crawler.pipelines.StoragePipeline': 300,
}

# Timeouts
DNS_TIMEOUT = 15
DOWNLOAD_TIMEOUT = 15
