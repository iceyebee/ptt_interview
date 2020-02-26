# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class PttInterviewItem(scrapy.Item):
    board_name = scrapy.Field()
    # define the fields for your item here like:
    authorId = scrapy.Field()
    authorName = scrapy.Field()
    title = scrapy.Field()
    publishedTime = scrapy.Field()
    content = scrapy.Field()
    canonicalUrl = scrapy.Field()
    createdTime = scrapy.Field()
    updateTime = scrapy.Field()
    comments = scrapy.Field()