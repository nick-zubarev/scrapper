# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from crawler.utils import Database
from crawler import settings


class StoragePipeline(object):
    """
    CSV Db manager
    """
    db = Database(settings.DB_FILENAME)

    def process_item(self, item, spider):
        """
        Process item
        :param item:
        :param spider:
        :return:
        """
        if not item['name']:
            return item

        self.db.manager.update_item(item=item, ratio=settings.MIN_MATCH_RATIO if settings.USE_MATCH_RATIO else None)
        return item

