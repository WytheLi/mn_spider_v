# -*- coding: utf-8 -*-
import json

import scrapy

from mn_spider_v import constants


class NbaMidSpider(scrapy.Spider):
    name = 'nba_mid'
    allowed_domains = ['matchweb.sports.qq.com']
    # start_urls = ['http://matchweb.sports.qq.com/']
    start_urls = ['https://matchweb.sports.qq.com/matchUnion/list?today=2019-11-22&startTime=%s&endTime=%s&columnId=100000&index=3&isInit=true&timestamp=1574245675333&callback=fetchScheduleListCallback100000' % (constants.START_TIME, constants.END_TIME)]
    custom_settings = {
        "ITEM_PIPELINES": {'mn_spider_v.pipelines.NbaMidPipeline': 300}
    }

    def parse(self, response):
        # print(response.text)
        fetchs_schedule_json = json.loads(response.text[32:-1])
        item = fetchs_schedule_json["data"]
        yield item
