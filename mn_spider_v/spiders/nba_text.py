# -*- coding: utf-8 -*-
import datetime
import json
from urllib import parse

import scrapy

from mn_spider_v import constants
from mn_spider_v.clients import mongo_conn, redis_conn
from mn_spider_v.common import gen_args_list


class NbaTextSpider(scrapy.Spider):
    name = 'nba_text'
    allowed_domains = ['matchweb.sports.qq.com']
    # https://matchweb.sports.qq.com/textLive/detail?competitionId=100000&matchId=54431803&AppName=kanbisai&AppOS=iphone&AppVersion=1.0&webVersion=1&ids=11963368_3626759963,11963367_3512631743,11963366_2076970808,11963365_2179851368,11963364_1908368926,11963360_442706471,11963356_479816278,11963353_2940670366,11963349_572884312,11963342_3127673888,11963338_4257560085,11963337_1723380495,11963334_26024958,11963328_1813330459,11963327_1890076601,11963326_2878742126,11963325_2446964875,11963324_1514821627,11963323_2793109401,11963319_3293359857&callback=textDetail
    start_time = redis_conn.get("start_time").decode()
    end_time = redis_conn.get("end_time").decode()
    # 将终止日期END_TIME +1天处理
    new_date_obj = datetime.datetime.strptime(end_time, "%Y-%m-%d") + datetime.timedelta(days=+1)
    new_date_str = datetime.datetime.strftime(new_date_obj, "%Y-%m-%d")

    text_keys_res = mongo_conn[constants.DB]["mn_sports_qq_nba_text_keys"].find(
        {"$and": [{"start_time": {"$gte": start_time}}, {"start_time": {"$lte": new_date_str}}]})
    # print(type(text_keys_res), isinstance(text_keys_res, Iterator))
    mid_dict_res = mongo_conn[constants.DB]["mn_sports_qq_nba_mid"].find(
        {"$and": [{"date": {"$gte": start_time}}, {"date": {"$lte": new_date_str}}]})
    # print(type(mid_dict_res), isinstance(mid_dict_res, Iterator))

    # find()返回迭代器
    # text_keys_res = list(text_keys_res)
    mid_dict_res = list(mid_dict_res)

    urls = []
    if text_keys_res and mid_dict_res:
        # 转化为判断一个值在不在字典列表里面
        # mid_dict_list = [mid_dict for mid_dict in mid_dict_res if keys_dict["_id"] == mid_dict["_id"]]
        for keys_dict in text_keys_res:
            for mid_dict in mid_dict_res:
                if keys_dict["_id"] == keys_dict["_id"]:
                    keys = keys_dict["data"]
                    # 拼接url参数
                    # python中取整： https://www.cnblogs.com/Devilf/p/8043033.html
                    # args_list = [",".join(keys[i * 20:(i + 1) * 20]) for i in range(0, math.ceil(len(keys) / 20))]
                    args_list = gen_args_list(keys)
                    # 列表反转
                    args_list = list(reversed(args_list))
                    for args in args_list:
                        url = "https://matchweb.sports.qq.com/textLive/detail?competitionId=%(competition_id)s&matchId=%(match_id)s&AppName=kanbisai&AppOS=iphone&AppVersion=1.0&webVersion=1&ids=%(ids)s&callback=textDetail&startTime=%(start_time)s&leftName=%(left_name)s&rightName=%(right_name)s" % {
                                "competition_id": mid_dict["data"]["mid"].split(":")[0],
                                "match_id": mid_dict["data"]["mid"].split(":")[1],
                                "ids": args,
                                "start_time": mid_dict["data"]["startTime"],
                                "left_name": mid_dict["data"]["leftName"],
                                "right_name": mid_dict["data"]["rightName"]
                            }
                        urls.append(url)
    # start_urls = ['http://matchweb.sports.qq.com/']
    start_urls = urls
    custom_settings = {
        "ITEM_PIPELINES": {'mn_spider_v.pipelines.NbaTextPipeline': 303},

        # 设置log日志
        'LOG_LEVEL': 'ERROR',
        'LOG_FILE': './logs/spider_nba_text.log'
    }

    def parse(self, response):
        print(response.url)
        if response.text == "textDetail([0,[],""]);":
            return
        query_string_list = response.url.split("?")[1].split("&")
        # url参数解码
        # from urllib import parse
        # parse.quote()编码；parse.unquote()解码
        start_time = parse.unquote(query_string_list[-3].split("=")[1])
        home_team_name = parse.unquote(query_string_list[-2].split("=")[1])
        away_team_name = parse.unquote(query_string_list[-1].split("=")[1])
        text_pagination = json.loads(response.text[11:-2])[1] if json.loads(response.text[11:-2])[1] else {}
        # for id, data in text_dict.items():
        print(text_pagination)
        # 图文直播数据请求到的分页数据为倒序
        # {"[id]": {}, "[id]: {}, "[id]": {}}
        yield {"data": text_pagination, "home_team_name": home_team_name, "away_team_name": away_team_name, "start_time": start_time}
