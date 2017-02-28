# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from bson import ObjectId
import pymongo


class MongoPipeline(object):
    def process_item(self, item, spider):
        item['_id'] = ObjectId(item['_id'])
        spider.insert(item)
        return item
