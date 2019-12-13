#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-6 下午4:52
# @Description: 常量

# 获取mid (爬虫爬取的日期)
# START_TIME = "2019-12-09"
# END_TIME = "2019-12-10"
# 线上用redis库保存

# mongo
# USERNAME = "root"
# PASSWORD = "Meanergy168"
# HOST = "139.129.229.223"
# PORT = 27017
# # DB = "mn_sports_qq_nba"
# # DB = "db_test"
# DB = "db_test_10"

# mongo
MONGO_USERNAME = "root"
MONGO_PASSWORD = "Meanergy168"
MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017
MONGO_DB = "db_test"

# mysql
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "Meanergy168"
MYSQL_HOST = "139.129.229.223"
MYSQL_PORT = 3306
MYSQL_DB = "mn_sports_qq_nba"

# redis
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = ""
REDIS_DB = 1

# chromedriver
# 本地win
# CHROMEDRIVER_PATH = r"C:\Users\WytheLi\Downloads\chromedriver.exe"
# 本地Ubuntu
CHROMEDRIVER_PATH = "/home/wytheli/Desktop/chromedriver"
# 线上
# CHROMEDRIVER_PATH = "/root/chromedriver"

# 头条用户
TT_USERNAME = "18229854080"
TT_PASSWORD = "Lzw1911@"

# 登录的用户列表 (需要存储用户对象，该列表全程应该存在于内存中)
login_user_list = []

# 单条图文发布 redis缓存24小时
TEXT_EXPIRY = 86400
TIME_NODE_EXPIRY = 86400

# 单条发送间隔 12分钟
TIME_LAG = 6

# 目标用户
user1 = {
    "username": "18229854080",
    "password": "Lzw1911@",
    "tag_team": "鹈鹕"  # ["凯尔特人"]
}

user2 = {
    "username": "19901551995",
    "password": "Fyy19920717",
    "tag_team": "76人"    # ["76人"]
}
