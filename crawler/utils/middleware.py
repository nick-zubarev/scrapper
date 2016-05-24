# Copyright (C) 2016 by wgear <invisliver@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import json
import time
import urllib2
from scrapy import log
from crawler import settings


class RandomProxy(object):
    """
    Speed match in hidemyass.com
    """
    SPD_MATCH = re.compile(r'width: (\d+)%.+')

    """
    Style classes match in hidemyass.com
    """
    CLASS_MATCH = re.compile(r'\.(.+?)\{display:(\w+)\}')

    conf = {
        'fast': getattr(settings, 'USE_FASTEST_PROXIES', False),
        'retry': getattr(settings, 'RELOAD_PROXIES_AFTER', 5),
        'min_speed': getattr(settings, 'FASTEST_PROXIES_MINIMAL_SPEED', 60),
        'retry_times': getattr(settings, 'RELOAD_PROXIES_TIMES', 5),
    }

    def __init__(self, load_proxy=False):
        """
        Load proxies
        :param conf:
        :return:
        """
        self.proxies = []
        self.use_proxy = load_proxy
        if self.use_proxy:
            self.load_new_proxies()

    def load_new_proxies(self):
        """
        Load while has not proxies loaded
        :return:
        """
        retries = self.conf['retry_times']
        while retries > 0 and len(self.proxies) == 0:
            time.sleep(self.conf['retry'])
            if self.conf['fast']:
                self.load_proxy_hidemyass()
            else:
                self.load_proxy_gimmeproxy()
            retries -= 1

        if not len(self.proxies) and self.conf['fast']:
            self.load_proxy_gimmeproxy()

        # Sort proxies
        self.proxies = sorted(self.proxies, key=lambda x: x['speed'], reverse=True)

    @classmethod
    def from_crawler(cls, crawler):
        """
        Start from crawler
        :param crawler:
        :return:
        """
        return cls(crawler.spider.use_proxy)

    def process_request(self, request, spider):
        """
        Rotate proxies
        :param request:
        :param spider:
        :return:
        """
        if hasattr(spider, 'use_proxy') and getattr(spider, 'use_proxy'):
            if 'proxy' in request.meta and request.meta['proxy'] in self.proxies:
                return

            # Load new proxies
            if not len(self.proxies):
                self.load_new_proxies()

            request.meta['proxy'] = self.proxies[0]['http']
        elif 'proxy' in request.meta:
            del request.meta['proxy']

    def process_exception(self, request, exception, spider):
        """
        Remove failed proxy and load new
        :param request:
        :param exception:
        :param spider:
        :return:
        """
        proxy = request.meta['proxy'] if 'proxy' in request.meta else None
        if proxy is None:
            return

        failed = None
        for x in self.proxies:
            if x['http'] == proxy:
                failed = x
                break

        # Remove failed proxy
        if failed in self.proxies:
            self.proxies.remove(failed)

        # Load new proxies
        if not len(self.proxies):
            self.load_new_proxies()

    def load_proxy_gimmeproxy(self):
        """
        Load proxy from gimmeproxy
        :return:
        """
        try:
            proxy = urllib2.urlopen('http://gimmeproxy.com/api/getProxy?get=true&supportsHttps=true&maxCheckPeriod=3600').read()
            self.proxies = [{'http': json.loads(proxy)['curl'], 'speed': 50}]
            log.msg('Loaded new proxy: {} with speed 50%'.format(self.proxies[0]['http']))
        except urllib2.HTTPError, e:
            log.msg('Proxy does not loaded: {}'.format(e.message))

    def load_proxy_hidemyass(self):
        """
        Load proxies from hidemyass.com
        :return:
        """
        try:
            from BeautifulSoup import BeautifulSoup
            proxies = urllib2.urlopen('http://proxylist.hidemyass.com/').read()
            body = BeautifulSoup(proxies)
            self.proxies = []
            for tr in body.findAll('tr', attrs={'class': 'altshade'}):
                try:
                    tds = tr.findAll('td')
                    spd = self._parse_spd(tds[4])
                    proto = tds[6].text.lower().strip()
                    if spd < self.conf['min_speed'] or proto not in ['http', 'https']:
                        continue

                    port = tds[2].text.strip()
                    ip = self._parse_ip(tds[1].find('span'), tds[1].find('style').text)
                    if not ip:
                        continue

                    self.proxies.append({'http': '{}://{}:{}'.format(proto, ip, port), 'speed': spd})
                except:
                    pass
            log.msg('Loaded {} new fast proxies: {}'.format(len(self.proxies), ', '.join(map(lambda x: x['http'] + ' [' + str(x['speed']) + ']', self.proxies))))
        except urllib2.HTTPError, e:
            log.msg('Fastest proxies does not loaded: {}'.format(e.message))
            log.msg('Try to get any proxy from gimmeproxy')
            self.load_proxy_gimmeproxy()

    def _parse_ip(self, ip_html, style):
        """
        Parse proxy ip on hidemyass
        :param ip_html:
        :param style:
        :return:
        """
        def is_int(val):
            try:
                int(val.text.strip())
                return True
            except:
                return False

        blocks = ip_html.findAll('span')

        # Clear display none
        blocks = filter(lambda x: 'none' not in x.get('style', ''), blocks)

        # Filter non integer
        blocks = filter(is_int, blocks)

        # Filter by class
        hidden = map(lambda x: x[0], filter(lambda x: 'none' in x[1], self.CLASS_MATCH.findall(style)))
        items = []
        for block in blocks:
            if block.get('class') in hidden:
                continue
            items.append(block.text)

        if len(items) != 4:
            return None

        return '.'.join(items)

    def _parse_spd(self, tr):
        """
        Parse proxy speed on hidemyass
        :param tr:
        :return:
        """
        div = str(tr.find('div', attrs={'class': 'indicator'})['style'])
        return int(self.SPD_MATCH.search(div).group(1))