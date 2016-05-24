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

    def abs_url(self, url):
        if 'oracle' in url: # Skip problem page
            return
        return super(StSpider, self).abs_url(url)

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

        # Try to parse company category
        try:
            category = body.find('li', attrs={'class': 'lvl-1 current'}).find('span', attrs={'itemprop': 'title'}).text
            company['category'] = [category.replace('...', '').strip()]
        except Exception, e:
            self.logger.error('Can not parse company category: {}'.format(e.message))

        # Try to parse company website
        try:
            website = body.find('span', attrs={'class': 'url'}).text.strip()
            company['website'] = website
        except Exception, e:
            self.logger.error('Can not parse company website: {}'.format(e.message))

        # Try to parse company locations
        try:
            locations = body.findAll('span', attrs={'itemprop': 'addressLocality'})
            company['location'] = [x.text.strip() for x in locations]
        except Exception, e:
            self.logger.error('Can not parse company location: {}'.format(e.message))

        # Try to get book now
        try:
            company['direct'] = 'Yes' if 'Book now' in response.body else 'No'
        except Exception, e:
            self.logger.error('Company {} does not booked'.format(company['name']))

        yield company