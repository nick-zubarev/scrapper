# -*- coding: utf-8 -*-
import scrapy
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

    db = Database(filename_csv=DB_FILENAME)

    PHONE_NUMBER_RE = re.compile(r'\+*\d{,3}\s*\(*\d{1,4}\)*\s*\d{3}\-\d{4}')

    USER_AGENT_LIST = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:10.0.2) Gecko/20100101 Firefox/10.0.2',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.186 Safari/535.1',
        'Mozilla/5.0 (X11; U; Linux i686; en; rv:1.9.0.11) Gecko/20080528 Epiphany/2.22 Firefox/3.0',
        'Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
        'Mozilla/5.0 (Windows NT 5.1; rv:8.0) Gecko/20100101 Firefox/8.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.8.1.4) Gecko/20070511 K-Meleon/1.1',
        'Opera/9.80 (X11; Linux i686; U; en-GB) Presto/2.6.30 Version/10.62',
        'Opera/9.50 (Macintosh; Intel Mac OS X; U; en)',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_1; zh-CN) AppleWebKit/530.19.2 (KHTML, like Gecko) Version/4.0.2 Safari/530.19',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.10) Gecko/2009043012 Songbird/1.2.0 (20090616030052)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.30 (KHTML, like Gecko) Comodo_Dragon/12.1.0.0 Chrome/12.0.742.91 Safari/534.30',
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Comodo_Dragon/4.1.1.11 Chrome/4.1.249.1042 Safari/532.5',
        'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; da-dk) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US) AppleWebKit/528.16 (KHTML, like Gecko, Safari/528.16) OmniWeb/v622.8.0.112941',
        'Mozilla/5.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0a2) Gecko/20111101 Firefox/9.0a2',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.11 Safari/535.19',
        'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    ]

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
        self.logger.debug('='*50)

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
                    'User-Agent': choice(self.USER_AGENT_LIST),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                formdata={
                    'criteria': json.dumps({
                        "companyName":{
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
                    'User-Agent': choice(self.USER_AGENT_LIST),
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
