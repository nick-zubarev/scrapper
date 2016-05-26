# -*- coding: utf-8 -*-
import json
import re
from urlparse import urlparse
from crawler.utils import Database
from crawler.settings import DB_FILENAME
from crawler.spiders import BaseSpider
from scrapy.http import FormRequest, Request
from BeautifulSoup import BeautifulSoup
from random import choice
from crawler.items import CompanyItem


class ZoomSpider(BaseSpider):
    name = "zoom"
    base_url = "http://zoominfo.com"
    allowed_domains = ["zoominfo.com"]

    PHONE_NUMBER_RE = re.compile(r'\+*\d{,3}\s*\(*\d{1,4}\)*\s*\d{3}\-\d{4}')

    def start_requests(self):
        """
        Loading database and try to find more information
        about company
        :return:
        """
        self.logger.debug('-'*50)
        self.logger.debug('Loading companies database from {}...'.format(DB_FILENAME))
        companies = self.db.iterate(lambda ln: self.db.dec(ln))
        companies = filter(lambda x: not x['phone'] or len(x['website']) < 7, companies)
        self.logger.debug('Loaded {} companies'.format(len(companies)))

        for comp in companies:
            search_term = comp['name']
            if len(comp['website'].strip()) > 7:
                search_term = urlparse(comp['website']).hostname

            yield FormRequest(
                url=self.abs_url('/s/search/company'),
                meta={'company': comp},
                method='POST',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Host': 'www.zoominfo.com',
                    'Origin': 'http://www.zoominfo.com',
                    'Pragma': 'no-cache',
                    'Referer': 'http://www.zoominfo.com/s/',
                    'User-Agent': choice(self.ua),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                formdata={
                    'criteria': json.dumps({
                        "companyName": {
                            "value": search_term,
                            "isUsed": 'true'
                        }
                    }),
                    'isCountOnly': json.dumps(False)
                }
            )

    def parse(self, response):
        """
        Parse zoominfo response
        :param response:
        :return:
        """
        self.logger.debug('-'*50)
        body = BeautifulSoup(response.body)
        company = response.meta['company']
        try:
            company_profile_page = body.find('td', attrs={'class': 'name'}).find('a')['href'].replace('#!', '')
            yield Request(
                url=self.abs_url(company_profile_page),
                meta={'company': response.meta['company']},
                callback=self.parse_info,
                headers={
                    'Host': 'www.zoominfo.com',
                    'Pragma': 'no-cache',
                    'Referer': 'http://www.zoominfo.com/s/',
                    'User-Agent': choice(self.ua),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            )
        except Exception, e:
            self.logger.debug('Detail information about {} was not found: {}'.format(
                company.get('name', 'Untitled'), e.message
            ))

    def parse_info(self, response):
        """
        Parse company information
        :param response:
        :return:
        """
        body = BeautifulSoup(response.body)
        company = response.meta['company']

        # Try to find company phone number
        if not company['phone']:
            try:
                phones = body.find('span', attrs={'class': 'companyContactNo'}).text
                company['phone'] = Database.COL_SEPARATOR.join(self.PHONE_NUMBER_RE.findall(phones))
            except Exception, e:
                self.logger.error('Can not parse company phone numbers: {}'.format(e.message))

        # Find website
        if not company['website']:
            try:
                company['website'] = body.find('div', attrs={'class': 'companyContact'}).find('a', attrs={'rel': 'NOFOLLOW'})['href']
            except Exception, e:
                self.logger.error('Can not parse company website: {}'.format(e.message))

        # Try to find company address
        if not company['location']:
            try:
                location = body.find('span', attrs={'class': 'companyAddress'}).text.strip()
                if location not in company['location']:
                    if isinstance(company['location'], list):
                        company['location'].append(location)
                    else:
                        company['location'] = [location]
            except Exception, e:
                self.logger.error('Can not parse company location: {}'.format(e.message))

        # Save company
        yield CompanyItem(company)
