#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 上午9:09
# @Description:
from celery import Celery

celery_app = Celery('celery_app')

celery_app.config_from_object("celery_tasks.config")
