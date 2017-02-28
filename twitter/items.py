# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TwitterItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = Field()
    tweet_id = Field()
    full_text = Field()
    user_id = Field()
    screen_name = Field()
    created_at = Field()
    crawled_at = Field()
