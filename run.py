#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-11 下午6:53
# @Description:  同时运行多个scrapy爬虫的几种方法
# 参考博客：https://www.cnblogs.com/rwxwsblog/p/4578764.html
import datetime
import time

from scrapy.crawler import CrawlerProcess

from mn_spider_v.clients import redis_conn
from mn_spider_v.spiders.nba_mid import NbaMidSpider
from mn_spider_v.spiders.nba_text import NbaTextSpider
from mn_spider_v.spiders.nba_text_keys import NbaTextKeysSpider
from mn_spider_v.spiders.nba_vs_info import NbaVsInfoSpider

process = CrawlerProcess()
process.crawl(NbaMidSpider)
process.crawl(NbaTextKeysSpider)
process.crawl(NbaVsInfoSpider)
process.crawl(NbaTextSpider)

while True:
    start_time = redis_conn.get("start_time")
    end_time = redis_conn.get("end_time")
    now_date = time.strftime("%Y-%m-%d", time.localtime())
    tomorrow_obj = datetime.datetime.strptime(now_date, "%Y-%m-%d") + datetime.timedelta(days=+1)
    tomorrow = datetime.datetime.strftime(tomorrow_obj, "%Y-%m-%d")
    if all([start_time, end_time]):
        start_time = start_time.decode()
        end_time = end_time.decode()
    else:
        # 初始化redis
        redis_conn.set("start_time", now_date)
        redis_conn.set("end_time", tomorrow)
        start_time = now_date
        end_time = tomorrow

    # 明确需要爬取今明两天的直播数据
    if now_date > start_time:
        redis_conn.set("start_time", now_date)
        redis_conn.set("end_time", tomorrow)
        start_time = now_date
        end_time = tomorrow

    process.start()  # the script will block here until all crawling jobs are finished