# -*- coding: utf-8 -*-
import scrapy


class StSpider(scrapy.Spider):
    name = "st"
    allowed_domains = ["springest.com"]
    start_urls = (
        'http://www.springest.com/',
    )

    def parse(self, response):
        pass
