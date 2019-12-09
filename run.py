#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 上午12:43
# @Description: scrapy定时启动多个爬虫 https://blog.csdn.net/qq_33042187/article/details/79023099
import datetime
import time
import os
from logging import getLogger

from mn_spider_v.constants import change_time, START_TIME

logger = getLogger(__name__)

while True:
    # now_date = time.strftime("%Y-%m-%d", time.localtime())
    # # 明确需要爬取今明两天的直播数据
    # if now_date > START_TIME:
    #     tomorrow_obj = datetime.datetime.strptime(now_date, "%Y-%m-%d") + datetime.timedelta(days=+1)
    #     tomorrow = datetime.datetime.strftime(tomorrow_obj, "%Y-%m-%d")
    #     change_time(now_date, tomorrow)

    print("######################### scrapy crawl nba_mid #########################")
    logger.info("scrapy crawl nba_mid")
    os.system("scrapy crawl nba_mid")

    print("######################### scrapy crawl nba_vs_info #########################")
    logger.info("scrapy crawl nba_vs_info")
    os.system("scrapy crawl nba_vs_info")

    print("######################### scrapy crawl nba_text_keys #########################")
    logger.info("scrapy crawl nba_text_keys")
    os.system("scrapy crawl nba_text_keys")

    print("######################### scrapy crawl nba_text #########################")
    logger.info("scrapy crawl nba_text")
    os.system("scrapy crawl nba_text")

    time.sleep(300)
