#!/usr/bin/env python
# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

screen_names = ['ubuntu']

def run_spiders():
    process = CrawlerProcess(get_project_settings())

    for screen_name in screen_names:
        kwargs = {
            'screen_name': screen_name
        }
        process.crawl('twitter', **kwargs)
    process.start()  # the script will block here until the crawling is finished
    process.stop()  # stopped?

if __name__ == '__main__':
    run_spiders()