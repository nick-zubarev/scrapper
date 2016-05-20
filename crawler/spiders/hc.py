# -*- coding: utf-8 -*-
import scrapy


class HcSpider(scrapy.Spider):
    name = "hc"
    allowed_domains = ["hotcourses.com"]
    start_urls = (
        'http://www.hotcourses.com/',
    )

    def parse(self, response):
        pass
