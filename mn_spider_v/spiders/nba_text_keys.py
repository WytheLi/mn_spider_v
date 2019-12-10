# -*- coding: utf-8 -*-
import json
from urllib import parse

import scrapy

from mn_spider_v import constants
from mn_spider_v.clients import mongo_conn, redis_conn
from mn_spider_v.common import gen_nba_vs_uuid


class NbaTextKeysSpider(scrapy.Spider):
    name = 'nba_text_keys'
    allowed_domains = ['matchweb.sports.qq.com']
    start_time = redis_conn.get("start_time").decode()
    end_time = redis_conn.get("end_time").decode()
    # 根据mid请求图文所需keys查询参数
    res = mongo_conn[constants.DB]["mn_sports_qq_nba_mid"].find(
        {"$and": [{"date": {"$gte": start_time}}, {"date": {"$lte": end_time}}]})
    urls = []
    if res:
        for sing_dict in res:
            urls.append("https://matchweb.sports.qq.com/textLive/index?competitionId=%(competition_id)s&matchId=%(match_id)s&AppName=kanbisai&AppOS=iphone&AppVersion=1.0&webVersion=1&callback=textIndexCallback&startTime=%(start_time)s&leftName=%(left_name)s&rightName=%(right_name)s" % {"competition_id": sing_dict["data"]["mid"].split(":")[0], "match_id": sing_dict["data"]["mid"].split(":")[1], "start_time": sing_dict["data"]["startTime"], "left_name": sing_dict["data"]["leftName"], "right_name": sing_dict["data"]["rightName"]})
    # https://matchweb.sports.qq.com/textLive/index?competitionId=100000&matchId=54431803&AppName=kanbisai&AppOS=iphone&AppVersion=1.0&webVersion=1&callback=textIndexCallback
    # start_urls = ['http://matchweb.sports.qq.com/']
    start_urls = urls
    custom_settings = {
        "ITEM_PIPELINES": {'mn_spider_v.pipelines.NbaTextKeysPipeline': 302},

        # 设置log日志
        'LOG_LEVEL': 'ERROR',
        'LOG_FILE': './logs/spider_nba_text_keys.log'
    }

    def parse(self, response):
        query_string_list = response.url.split("?")[1].split("&")
        # url参数解码
        # from urllib import parse
        # parse.quote()编码；parse.unquote()解码
        start_time = parse.unquote(query_string_list[-3].split("=")[1])
        home_team_name = parse.unquote(query_string_list[-2].split("=")[1])
        away_team_name = parse.unquote(query_string_list[-1].split("=")[1])
        text_index_json = json.loads(response.text[18:-2])
        keys = text_index_json[1]
        uuid = gen_nba_vs_uuid(home_team_name, away_team_name, start_time)
        yield {"_id": uuid, "data": keys, "home_team_name": home_team_name, "away_team_name": away_team_name, "start_time": start_time}
