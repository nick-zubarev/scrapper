# -*- coding: utf-8 -*-
import scrapy


class TgSpider(scrapy.Spider):
    name = "tg"
    allowed_domains = ["courses.theguardian.com"]
    start_urls = (
        'http://www.courses.theguardian.com/',
    )

    def parse(self, response):
        pass
