from __future__ import unicode_literals
import scrapy
from urlparse import urlparse


class BaseSpider(scrapy.Spider):
    # Base URL for make absolute URL from URI
    base_url = 'http://www.hotcourses.com'

    # Use proxy for this spider
    use_proxy = False

    def __init__(self, name=None, noproxy=False, proxy=False, **kwargs):
        if bool(noproxy) is True:
            self.use_proxy = False
        if bool(proxy) is True:
            self.use_proxy = True
        super(BaseSpider, self).__init__(name, **kwargs)

    def abs_url(self, url):
        """
        Make absolute url
        :param url:
        :return:
        """
        url_data = urlparse(url)
        return '{}{}?{}'.format(self.base_url, url_data.path, url_data.query)
