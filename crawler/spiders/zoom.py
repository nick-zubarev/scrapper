# -*- coding: utf-8 -*-
import scrapy


class ZoomSpider(scrapy.Spider):
    name = "zoom"
    allowed_domains = ["zoominfo.com"]
    start_urls = (
        'http://www.zoominfo.com/',
    )

    def parse(self, response):
        pass
