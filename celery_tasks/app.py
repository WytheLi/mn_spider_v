#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 上午9:11
# @Description:
from celery import Celery

# 添加celery_tasks目录到解释器导包路径

celery_app = Celery('celery_app', broker='redis://127.0.0.1/0')
