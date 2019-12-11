#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-11 下午6:53
# @Description:  同时运行多个scrapy爬虫的几种方法
# 参考博客：https://www.cnblogs.com/rwxwsblog/p/4578764.html


from scrapy.crawler import CrawlerProcess

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
    process.start()  # the script will block here until all crawling jobs are finished