#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 上午12:43
# @Description: 多账号测试
import time

from celery_tasks.publish.tasks import publish_text

publish_text.delay("18229854080", "Lzw1911@", "乡村一把手呀一把手")
time.sleep(2)
publish_text.delay("19901551995", "Fyy19920717", "乡村一把手呀一把手")

time.sleep(360)
publish_text.delay("18229854080", "Lzw1911@", "乡村二把手呀二把手")
time.sleep(2)
publish_text.delay("19901551995", "Fyy19920717", "乡村二把手呀二把手")

time.sleep(360)
publish_text.delay("18229854080", "Lzw1911@", "乡村三把手呀三把手")
time.sleep(2)
publish_text.delay("19901551995", "Fyy19920717", "乡村三把手呀三把手")


time.sleep(360)
publish_text.delay("18229854080", "Lzw1911@", "乡村四把手呀四把手")
time.sleep(2)
publish_text.delay("19901551995", "Fyy19920717", "乡村四把手呀四把手")
