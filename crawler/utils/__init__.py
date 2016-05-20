#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import requests
from fuzzywuzzy import fuzz
from crawler import settings


class Manager(object):
    """
    DB Manager
    """

    def __init__(self, db):
        """
        Create new manager instance
        :param db:
        :return:
        """
        if not isinstance(db, Database):
            raise ValueError('db parameter is not Database instance')

        self.db = db
        self._create_headers()

    def _create_headers(self):
        """
        Creation CSV headers
        :return:
        """
        if not os.path.getsize(self.db.output):
            headers = map(lambda x: x['verbose'], self.db.HEADERS.values())
            self.db.append(self.db.CSV_SEPARATOR.join(headers) + '\n')

    def update_item(self, item, search_by=settings.PRIMARY_FIELD, ratio=None):
        """
        Update item
        :param item:
        :return:
        """
        term = item.get(search_by)
        output_lines = []
        updated_item = False
        fhandler = open(self.db.output, 'rw+')
        for ln in fhandler.readlines():
            data = self.db.dec(ln)
            # Update row if found
            if data.get(search_by):
                if ratio is None and data.get(search_by) == term:
                    ln = self.db.enc(self.merge(data, item))
                    updated_item = True
                elif ratio and fuzz.partial_ratio(data.get(search_by), term) >= ratio:
                    ln = self.db.enc(self.merge(data, item))
                    updated_item = True

            # Write line
            output_lines.append(ln)
        fhandler.close()

        # Create item
        if not updated_item:
            self.db.append(self.db.enc(item))
            return True

        # Write data
        fhandler = open(self.db.output, 'w')
        fhandler.writelines(output_lines)
        return True

    def get(self, search_term, by=settings.PRIMARY_FIELD):
        """
        Strong matching with 100% ratio
        :param search_term:
        :param by:
        :return:
        """
        if not search_term:
            return

        fhandler = open(self.db.output, 'r')
        for ln in fhandler.readlines():
            data = self.db.dec(ln)
            if data.get(by) and search_term == data.get(by):
                yield data
        fhandler.close()

    def match(self, search_term, by=settings.PRIMARY_FIELD, ratio=95):
        """
        Search item with match ratio
        :param search_term:
        :param by:
        :param ratio:
        :return:
        """
        if not search_term:
            return

        fhandler = open(self.db.output, 'r')
        for ln in fhandler.readlines():
            data = self.db.dec(ln)
            if data.get(by) and fuzz.partial_ratio(search_term, data.get(by)) >= ratio:
                yield data
        fhandler.close()

    def merge(self, item1, item2):
        """
        Merge items
        :param item1:
        :param item2:
        :return:
        """
        item = item1
        for k, v in item2.iteritems():
            if self.db.col_data(k).get('list'):
                item[k] += v
                continue
            item[k] = v

        print '-' * 200
        print '-' * 20, 'Merging'
        print 'source', item1
        print 'target', item2,
        print 'result', item
        return item


class Database(object):
    """
    Project root directory
    """
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    """
    Separator for csv output file
    """
    CSV_SEPARATOR = ","
    COL_SEPARATOR = " | "

    """
    Headers list
    """
    HEADERS = {
        0: {
            'name': 'name',
            'verbose': 'Company Name',
            'default': ''
        },
        1: {
            'name': 'email',
            'verbose': 'E-Mail',
            'default': ''
        },
        2: {
            'name': 'phone',
            'verbose': 'Phone Number',
            'default': ''
        },
        3: {
            'name': 'website',
            'verbose': 'Website',
            'default': ''
        },
        4: {
            'name': 'direct',
            'verbose': 'Direct book',
            'default': 'No'
        },
        5: {
            'name': 'category',
            'verbose': 'Categories',
            'list': True,
            'default': ''
        },
        6: {
            'name': 'location',
            'verbose': 'Locations',
            'list': True,
            'default': ''
        },
    }

    def __init__(self, filename_csv='database.csv'):
        """
        Initialize database
        :param filename_csv:
        :return:
        """
        if not os.path.exists(os.path.join(self.ROOT_DIR, filename_csv)):
            raise ValueError("Output file %s doesn't exists" % os.path.join(self.ROOT_DIR, filename_csv))

        self.output = os.path.join(self.ROOT_DIR, filename_csv)
        self.manager = Manager(self)

    def col_data(self, name):
        """
        Get header info
        :param name:
        :return:
        """
        for i in self.HEADERS.values():
            if i['name'] == name:
                return i
        return {}

    def write(self, lines=None):
        """
        Write lines
        :param lines:
        :return:
        """
        fhandler = file(self.output, 'w')
        fhandler.writelines(lines if isinstance(lines, list) else [])
        return fhandler.close()

    def iterate(self, func):
        """
        Iterate lines
        :param func:
        :return:
        """
        fhandler = file(self.output, 'r')
        lines = []
        for ln in fhandler.readlines():
            lines.append(func(ln))
        fhandler.close()
        return lines

    def update(self, func):
        """
        Update lines
        :param func:
        :return:
        """
        lines = self.iterate(func)
        return self.write(lines)

    def append(self, line):
        """
        Append line
        :param line:
        :return:
        """
        fhandler = file(self.output, 'a')
        fhandler.write(line)
        return fhandler.close()

    @staticmethod
    def defaults():
        """
        Default dictionary for row
        :return:
        """
        default_dict = {}
        for i, dcol in Database.HEADERS.iteritems():
            default_dict[dcol['name']] = dcol.get('default', '')

        return default_dict

    def enc(self, dictionary):
        """
        Encode line
        :param dictionary:
        :return:
        """
        return self.CSV_SEPARATOR.join([
            self.clen(dictionary.get('name', '')),
            self.clen(dictionary.get('email', '')),
            self.clen(dictionary.get('phone', '')),
            self.clen(dictionary.get('website', '')),
            self.clen(dictionary.get('direct', 'No')),
            self.COL_SEPARATOR.join(self.clen(dictionary.get('category', []))),
            self.COL_SEPARATOR.join(self.clen(dictionary.get('location', []))),
        ]) + '\n'

    def dec(self, line):
        """
        Decode line
        :param dictionary:
        :return:
        """
        dictionary = {}
        for i, col in enumerate(line.split(self.CSV_SEPARATOR)):
            dcol = self.HEADERS.get(i, {'name': 'unknown', 'verbose': 'Unknown'})

            value = col
            if dcol.get('list') is True:
                value = col.split(self.COL_SEPARATOR)

            dictionary[dcol['name']] = value
        return dictionary

    def clen(self, string):
        """
        Clean entity
        :param string:
        :return:
        """
        clean = lambda x: x.replace(self.CSV_SEPARATOR, '').replace(self.COL_SEPARATOR, '').strip()
        if isinstance(string, list):
            return map(clean, self.unique_list(string))
        return clean(string)

    def unique_list(self, lst):
        """
        Unique list items
        :param lst:
        :return:
        """
        result = []
        for i in lst:
            if i in lst: continue
            if not len(i.strip()): continue
            result.append(i)
        return result

def proxy_get_url(url, proxy):
    """
    Load url with proxy
    :param url:
    :param proxy:
    :return:
    """
    return requests.get(
        url=url,
        proxies={"http": proxy},
        allow_redirects=False,
        timeout=settings.DOWNLOAD_TIMEOUT
    ).text
