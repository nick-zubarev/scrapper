# -*- coding: utf-8 -*-
from crawler.spiders import BaseSpider
from BeautifulSoup import BeautifulSoup
from scrapy.http import Request
from crawler.items import CompanyItem
from crawler.utils import Database


class StSpider(BaseSpider):
    name = "st"
    allowed_domains = ["springest.com", "www.springest.com"]
    base_url = "https://www.springest.com"
    start_urls = (
        'https://www.springest.com/all-providers',
    )

    use_proxy = False

    def parse(self, response):
        """
        Parse companies
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)

        for item in body.find('ul', attrs={'class': 'logo-list'}).findAll('li'):
            com_uri = item.find('a')['href']
            if com_uri == '/': # skip invalid company url
                continue

            yield Request(
                url=self.abs_url(com_uri),
                callback=self.parse_item,
                meta={
                    'title': item.find('img')['title']
                }
            )
            break

    def parse_item(self, response):
        """
        Parse item response
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)
        company = CompanyItem(Database.defaults())
        meta = response.meta

        company['name'] = ' '.join(meta['title'].split(' ')[1:])
        print company