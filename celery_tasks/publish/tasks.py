#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 上午9:34
# @Description:
from celery_tasks import celery_app
from mn_spider_v.constants import login_user_list
from mn_spider_v.publish_content import TouTiaoLogin, TouTiaoPosted


@celery_app.task(name='publish_text')
def publish_text(username, password, content):
    """
    celery异步发送
    :param username:
    :param password:
    :param content:
    :return:
    """
    # TODO cookie过期还没有处理
    user = None
    if not login_user_list:     # 列表为空
        user = TouTiaoLogin(username, password)
        user.login()
        login_user_list.append(user)
    else:
        for user in login_user_list:
            if user.username == username:
                print(user.username)
                user = user
                break
        else:
            user = TouTiaoLogin(username, password)
            user.login()
            login_user_list.append(user)

    # user = TouTiaoLogin(cd, "19901551995", "Fyy19920717")
    # print(user.cookies)
    p = TouTiaoPosted(user.chromedriver, user.cookies)
    p.posted(content)
