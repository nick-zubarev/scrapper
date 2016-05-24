# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from crawler.spiders import BaseSpider
from BeautifulSoup import BeautifulSoup
from scrapy.http import Request
from crawler.utils import Database, proxy_get_url
from crawler.items import CompanyItem


class TgSpider(BaseSpider):
    name = "tg"
    base_url = "http://courses.theguardian.com"
    allowed_domains = ["courses.theguardian.com"]

    start_urls = (
        'http://courses.theguardian.com/',
    )

    use_proxy = False

    def parse(self, response):
        """
        Parse categories
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)
        for category in body.findAll('li', attrs={'class': 'facet-links__item column__item'}):
            link = category.find('a')
            yield Request(
                url=self.abs_url(link['href']),
                callback=self.parse_category,
                meta={
                    'category': link.text.strip()
                }
            )

    def parse_category(self, response):
        """
        Parse category pagination
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)

        # Parse items
        for item in body.findAll('a', attrs={'class': 'course-block__lister-item-link'}):
            yield Request(
                url=self.abs_url(item['href']),
                callback=self.parse_item,
                meta=response.meta
            )

        # Try to parse next page
        next_page = body.find('link', attrs={'rel': 'next'})
        if next_page:
            yield Request(
                url=next_page['href'],
                callback=self.parse_category,
                meta=response.meta
            )

    def parse_item(self, response):
        """
        Parse company item
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)
        company = CompanyItem(Database.defaults())

        # Try to parse company name
        try:
            company['name'] = body.find('a', attrs={'class': 'course-block__provider-link'}).text.strip()
        except Exception, e:
            self.logger.error('Can not parse company name: {}'.format(e.message))
            return

        # Try to parse company category
        try:
            company['category'] = [response.meta['category']]
        except Exception, e:
            self.logger.error('Can not parse company category: {}'.format(e.message))

        # Try to parse locations
        try:
            company['location'] = [body.find('td', attrs={'data-label': 'Location'}).text.strip()]
        except Exception, e:
            self.logger.error('Can not parse company location: {}'.format(e.message))

        # Try to parse company phone number
        try:
            company['phone'] = body.find('span', attrs={'class': 'contact-details__phoneno'}).text.strip()
        except Exception, e:
            self.logger.error('Can not parse company phone number: {}'.format(e.message))

        # Try to parse company website
        try:
            website_proxy = body.find('a', attrs={'class': 'contact-details__website icon-before one-whole'})['href']
            company['website'] = self.get_website_url(
                self.abs_url(website_proxy)
            )
        except Exception, e:
            self.logger.error('Can not parse company website: {}'.format(e.message))

        yield company

    def get_website_url(self, proxy):
        """
        Parse website URL from proxy page
        :param proxy:
        :return:
        """
        body = BeautifulSoup(
            proxy_get_url(proxy)
        )

        refresh_meta = body.find('meta', attrs={'http-equiv': 'refresh'})['content']
        return refresh_meta.split('=')[-1].strip()
