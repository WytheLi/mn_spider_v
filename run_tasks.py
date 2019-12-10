#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 下午6:40
# @Description: delay测试
import time

from celery_tasks.publish.tasks import publish_text


res1 = publish_text.delay("18229854080", "Lzw1911@", "曾今，意外")
print(res1, res1.id, res1.status)
time.sleep(5)
res2 = publish_text.delay("18229854080", "Lzw1911@", "他和她相爱")
print(res2, res2.id, res2.status)

print("任务发出...")

# 在redis中获取 &
# celery-task-meta-[res1.id]
