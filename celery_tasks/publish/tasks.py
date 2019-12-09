#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-9 上午9:34
# @Description:
from celery_tasks.app import celery_app
from mn_spider_v.publish_content import TouTiaoLogin, TouTiaoPosted

auth_user_list = []


@celery_app.task(name='publish_text')
def publish_text(username, password, content):
    """
    celery异步发送
    :param username:
    :param password:
    :param content:
    :return:
    """
    user = None
    print(auth_user_list)
    if not auth_user_list:
        user = TouTiaoLogin(username, password)
        user.login()
        auth_user_list.append(user)
    else:
        for user in auth_user_list:
            if user.username == username:
                print(user.username)
                user = user
                break
        else:
            user = TouTiaoLogin(username, password)
            user.login()
            auth_user_list.append(user)
    # user = TouTiaoLogin(cd, "19901551995", "Fyy19920717")
    # print(user.cookies)
    p = TouTiaoPosted(user.chromedriver, user.cookies)
    p.posted(content)
