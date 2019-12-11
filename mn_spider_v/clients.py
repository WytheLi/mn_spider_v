#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-6 下午5:27
# @Description: 数据库连接对象
import pymysql
import redis
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

# 创建redis连接池
redis_conn_pool = redis.ConnectionPool(host=constants.REDIS_HOST, port=constants.REDIS_PORT, db=constants.REDIS_DB)
# 创建连接对象
redis_conn = redis.Redis(connection_pool=redis_conn_pool)


if __name__ == "__main__":
    # 字符串操作
    # redis_conn.set("start_time", "2019-10-10")
    # res1 = redis_conn.get("start_time").decode()
    # print(res1)
    redis_conn.setex("time_node_aaa", 300, "aaaa")


    # 列表操作
    # redis_conn.lpush("login_user_list", "aaa")
    # redis_conn.lpush("login_user_list", "bbb")
    # list_len = redis_conn.llen("login_user_list")
    # print(list_len)
    # res_list = redis_conn.lrange("login_user_list", 0, list_len-1)
    # print(res_list)
