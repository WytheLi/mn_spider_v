#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-6 下午4:52
# @Description: 常量

# 获取mid
START_TIME = "2019-12-04"
END_TIME = "2019-12-05"

# mongo
USERNAME = "root"
PASSWORD = "Meanergy168"
HOST = "139.129.229.223"
PORT = 27017
# DB = "mn_sports_qq_nba"
# DB = "db_test"
DB = "db_demo"

# mysql
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "Meanergy168"
MYSQL_HOST = "139.129.229.223"
MYSQL_PORT = 3306
MYSQL_DB = "mn_sports_qq_nba"

# chromedriver
# 本地win
# CHROMEDRIVER_PATH = r"C:\Users\WytheLi\Downloads\chromedriver.exe"
# 本地Ubuntu
CHROMEDRIVER_PATH = "/home/wytheli/Desktop/chromedriver"
# 线上
# CHROMEDRIVER_PATH = "/root/chromedriver"

# 已登录的用户对象列表
USER_LIST = []

# 头条用户
TT_USERNAME = "18229854080"
TT_PASSWORD = "Lzw1911@"


def change_time(start_time, end_time):
    """
    变更需要爬虫爬取的日期
    :param start_time:
    :param end_time:
    :return:
    """
    global START_TIME
    global END_TIME
    START_TIME = start_time
    END_TIME = end_time
