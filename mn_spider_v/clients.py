#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-6 下午5:27
# @Description: 数据库连接对象
import pymysql
from pymongo import MongoClient

from mn_spider_v import constants

mongo_conn = MongoClient(host=constants.HOST, port=constants.PORT, username=constants.USERNAME,
                         password=constants.PASSWORD)
# client = MongoClient(host=config.HOST, port=config.PORT, username=config.USERNAME, password=config.PASSWORD, retryWrites=False)
db = mongo_conn[constants.DB]

mysql_conn = pymysql.connect(
    host=constants.MYSQL_HOST,
    user=constants.MYSQL_USERNAME,
    password=constants.MYSQL_PASSWORD,
    db=constants.MYSQL_DB,
    charset='utf8mb4'
)
