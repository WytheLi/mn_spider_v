#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 下午3:57
# @Description: celery自定义日志输出　https://blog.csdn.net/DongGeGe214/article/details/85686479

BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'

# 任务导入
CELERY_IMPORTS = (
    'celery_tasks.publish.tasks',
)
