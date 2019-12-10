#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 下午4:55
# @Description: celery启动worker 用于测试
import os
os.system("celery -A celery_tasks worker -l info")
# celery worker --app=app.app --concurrency=1 --loglevel=INFO
# 线上运行下面
# os.system("celery -D -A celery_tasks worker -l info -f logs/celery.log")
