# -*- coding: utf-8 -*-
import json

import scrapy

from mn_spider_v.clients import redis_conn


class NbaMidSpider(scrapy.Spider):
    name = 'nba_mid'
    allowed_domains = ['matchweb.sports.qq.com']
    # start_urls = ['http://matchweb.sports.qq.com/']
    start_time = redis_conn.get("start_time").decode()
    end_time = redis_conn.get("end_time").decode()
    start_urls = ['https://matchweb.sports.qq.com/matchUnion/list?today=2019-11-22&startTime=%s&endTime=%s&columnId=100000&index=3&isInit=true&timestamp=1574245675333&callback=fetchScheduleListCallback100000' % (start_time, end_time)]
    custom_settings = {
        "ITEM_PIPELINES": {'mn_spider_v.pipelines.NbaMidPipeline': 300},

        # 设置log日志
        'LOG_LEVEL': 'ERROR',
        'LOG_FILE': './logs/spider_nba_mid.log'
    }

    def parse(self, response):
        # print(response.text)
        fetchs_schedule_json = json.loads(response.text[32:-1])
        item = fetchs_schedule_json["data"]
        yield item
