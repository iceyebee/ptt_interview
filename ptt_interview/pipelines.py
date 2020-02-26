# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import logging
from scrapy.exceptions import DropItem

class MongoDBPipeline(object):

    collection = 'output'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'ptt_interview')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        #insert data
        #if repeated, do not insert
        if valid:
            self.db[self.collection].update({'canonicalUrl': item['canonicalUrl']}, dict(item), upsert=True)            #self.db[self.collection].update({'thread_url': item['thread_url']}, {$set: dict(item)}, {upsert: true})
            logging.debug("Added to MongoDB database!")
        return item
