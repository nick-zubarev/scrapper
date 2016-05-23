# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy.http import Request
from BeautifulSoup import BeautifulSoup
from crawler.items import CompanyItem
from crawler.spiders import BaseSpider
from crawler.utils import Database, proxy_get_url
from random import random
from urllib2 import urlopen


class HcSpider(BaseSpider):
    name = "hc"
    allowed_domains = []
    base_url = 'http://www.hotcourses.com'
    start_urls = (
        'http://www.hotcourses.com/courses/',
    )

    use_proxy = True

    def parse(self, response):
        """
        Parse pagination
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)
        for item in body.findAll('div', attrs={'class': 'al_glr fl'}):
            # Get main category
            heading = item.find('h4', attrs={'class': 'glr_hd'}).text

            # Get subcategories and schedule requests
            for sub in item.findAll('li'):
                subcategory = sub.find('a')

                yield Request(
                    url=self.abs_url(subcategory['href']),
                    callback=self.parse_subcategory_pagination,
                    meta={
                        'page': 1,
                        'base_url': subcategory['href'],
                        'category': [heading, subcategory.text]
                    }
                )

    def parse_subcategory_pagination(self, response):
        """
        Parse response of subcategory
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)
        metadata = response.meta

        self.logger.debug('Parse category {} page {}'.format(metadata['category'][-1], metadata['page']))

        # Parse items
        for item in body.findAll('a', attrs={'class': 'crsnm crs_ti'}):
            yield Request(
                url=self.abs_url(item['href']),
                callback=self.parse_item,
                meta=metadata
            )

        # Schedule next page
        next_page = body.find('a', attrs={'id': 'dNextPg'})
        if next_page:
            metadata['page'] += 1
            yield Request(
                url='{}?p={}'.format(self.abs_url(metadata['base_url']), metadata['page']),
                callback=self.parse_subcategory_pagination,
                meta=metadata
            )

    def parse_item(self, response):
        """
        Parse item data
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)
        company = CompanyItem(Database.defaults())

        # Parse company name
        try:
            company['name'] = body.find('h1').find('span').text.strip()
        except Exception, e:
            self.logger.error('Can not parse company name: {}'.format(e.message))

        # Set categories
        company['category'] = response.meta['category']

        # Parse company website
        try:
            company['website'] = self.website_url(body.find('a', attrs={'class': 'btn bweb vwo_vweb'})['onclick'], response.meta['proxy'])
        except Exception, e:
            self.logger.error('Can not parse company website: {}'.format(e.message))

        # Parse company location
        try:
            location_description = [x.text.strip() for x in body.findAll('p', attrs={'class': 'qkas ml26'})]
            location_description = [location_description[-1]] if len(location_description) else []
            location_table = [
                unicode(x).split('<div class="ven-tip">')[0].split('\n')[1].strip()
                for x in body.findAll('td', attrs={'data-title': 'Location'})
            ]

            company['location'] = location_table if len(location_table) else location_description
        except Exception, e:
            self.logger.error('Can not parse company location: {}'.format(e.message))

        # Chek is company booked
        try:
            company['direct'] = 'Yes' if body.find('div', attrs={'id': 'cdStkyBkBtnHdn'}) else 'No'
        except Exception, e:
            self.logger.error('Can not parse company direct booked: {}'.format(e.message))

        yield company

    def website_url(self, call, proxy=None):
        """
        Get website url
        :param call:
        :return:
        """
        call = call.split(';')[0].replace("'", '').replace('getwebsiteUrl (', '').replace(')', '').split(',')
        params = {
            'suborder': call[0],
            'addressType': call[1],
            'randNum': int(random() * 100000000),
            'oppId': call[4],
            'courseId': call[5],
            'intType': call[6] if len(call) > 6 else ''
        }

        ws_uri = "/pls/cgi-bin/get_website_url_prc?p_suborder_item={suborder}" \
              "&p_address_type_id={addressType}&rn={randNum}&p_opportunity_id={oppId}" \
              "&w={courseId}&p_int_type={intType}".format(**params)

        self.logger.debug('Trying to get website url <GET {}>'.format(self.abs_url(ws_uri)))

        if proxy is None:
            content = urlopen(self.abs_url(ws_uri), timeout=4).read()
        else:
            content = proxy_get_url(self.abs_url(ws_uri), proxy)

        content = BeautifulSoup(content)
        return content.find('link', attrs={'rel': 'shortlink'})['href']
