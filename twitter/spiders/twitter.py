
#!/usr/bin/env python
# coding:utf-8

import urllib
import json
import datetime

import pymongo
from bson import ObjectId
import requests
import scrapy
from scrapy.spiders.init import InitSpider
from scrapy.http import Request
from scrapy.http.headers import Headers
from dateutil import parser

from ..items import TwitterItem
from ..config import *

authorization_token = None
guest_token = None

client = pymongo.MongoClient(MONGODB_ADDR)
db = client[MONGODB_DB]
if MONGODB_AUTH:
    db.authenticate(MONGODB_USER, MONGODB_PWD)

class TwitterSpider(InitSpider):
    name = "twitter"
    is_mobile = True

    url_base = 'https://mobile.twitter.com/'
    screen_name = ''
    user_info = {}

    def __init__(self, **kw):
        super(TwitterSpider, self).__init__(**kw)
        self.screen_name = kw['screen_name']
        self.collection = db['tweets']

    def insert(self, item):
        if not self.collection.find_one({'tweet_id': item['tweet_id']}):
            self.collection.insert_one(dict(item))

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.url_base + self.screen_name, callback=self.extract_token)

    def extract_token(self, response):
        global authorization_token
        global guest_token
        for cookie in response.headers.getlist('Set-Cookie'):
            k, v = cookie.split(";")[0].split("=")
            if k == 'gt':
                guest_token = v
                break
        self.logger.info('guest_token: %s', guest_token)
        script_url = response.css('body script:last-child::attr(src)').extract()[0]
        self.logger.info('script url: %s', script_url)
        r = requests.get(script_url, headers={'Referer': response.url})
        content = r.content
        key = 'BEARER_TOKEN:"'
        start = content.index(key)
        end = content.index('",', start)
        authorization_token = content[start + len(key) : end]
        self.logger.info('token: %s', authorization_token)

        query = urllib.urlencode({
            "include_blocking": "true",
            "include_blocked_by": "true",
            "include_can_dm": "true",
            "include_followed_by": "true",
            "include_mute_edge": "true",
            "skip_status": "true",
            "screen_name": self.screen_name,
            "include_profile_interstitial_type": "true",
        })
        show = 'https://api.twitter.com/1.1/users/show.json?%s' % query
        return AuthTokenRequest(show, callback=self.get_user_info)

    def get_user_info(self, response):
        self.user_info = json.loads(response.text)
        self.logger.info('user id: %d', self.user_info['id'])
        query = urllib.urlencode({
            "cards_platform": "Web-12",
            "include_cards": "1",
            "include_ext_media_color": "true",
            "tweet_mode": "extended",
            "earned": "1",
            "pc": "1",
            "id": self.user_info['id'],
            "count": "20",
            "exclude_pinned_tweets": "true",
            "include_tweet_replies": "true",
        })
        user = 'https://api.twitter.com/1.1/timeline/user.json?%s' % query
        return AuthTokenRequest(user, callback=self.get_timeline)

    def get_timeline(self, response):
        data = json.loads(response.text)
        for _id, tweet in data['twitter_objects']['tweets'].iteritems():
            item = TwitterItem()
            item['_id'] = str(ObjectId())
            item['tweet_id'] = _id
            item['full_text'] = tweet['full_text']
            item['user_id'] = self.user_info['id']
            item['screen_name'] = self.screen_name
            item['created_at'] = parser.parse(tweet['created_at'])
            item['crawled_at'] = datetime.datetime.utcnow()
            yield item

class AuthTokenRequest(Request):
    @property
    def headers(self):
        global authorization_token
        return Headers({
            'Authorization': 'Bearer {}'.format(authorization_token),
            'x-guest-token': guest_token
            }, encoding=self.encoding)

    @headers.setter
    def headers(self, value):
        pass
