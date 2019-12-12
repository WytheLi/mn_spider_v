#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-7 下午2:19
# @Description: 公共函数
import datetime
import hashlib
import math
import re

from mn_spider_v import constants
from mn_spider_v.clients import mysql_conn, redis_conn
from celery_tasks.publish.tasks import publish_text


def save_text_after_game_to_mysql(uuid, text, home_team, away_team, start_time):
    """
    保存赛后文本到mysql
    :param text:
    :return:
    """
    with mysql_conn.cursor() as cursor:
        # 外鍵關聯的表，插入數據時，關聯項數據在被關聯表中必須先存在
        save_vs_text = """
            insert into mn_sports_qq_nba_text_after_game(id, home_team, away_team, start_time, text) values (%(uuid)s, %(home_team)s, %(away_team)s, %(start_time)s, %(text)s)
        """
        cursor.execute(save_vs_text,
                       {"uuid": uuid, "home_team": home_team, "away_team": away_team,
                        "start_time": start_time, "text": text})
        mysql_conn.commit()


def save_text_before_game_to_mysql(uuid, text, home_team, away_team, start_time):
    """
    保存赛前文本到mysql
    :param vs:
    :param text:
    :return:
    """
    with mysql_conn.cursor() as cursor:
        # 外鍵關聯的表，插入數據時，關聯項數據在被關聯表中必須先存在
        save_vs_text = """
            insert into mn_sports_qq_nba_text_before_game(id, home_team, away_team, start_time, text) values (%(uuid)s, %(home_team)s, %(away_team)s, %(start_time)s, %(text)s)
        """
        cursor.execute(save_vs_text,
                       {"uuid": uuid, "home_team": home_team, "away_team": away_team,
                        "start_time": start_time, "text": text})
        mysql_conn.commit()


def gen_nba_vs_uuid(home_team_name, away_team_name, start_time):
    """
    生成uuid
    :return:
    """
    string = home_team_name + "vs" + away_team_name + start_time
    if isinstance(string, str):
        obj = hashlib.md5(string.encode())
    else:
        raise TypeError()
    res = obj.hexdigest()
    return res


def gen_args_list(keys):
    """
    列表推导式有独立的作用域
    固这里用函数
    :param keys:
    :return:
    """
    # [",".join(keys[i * 20:(i + 1) * 20]) for i in range(0, math.ceil(len(keys) / 20))]
    temp = []
    for i in range(0, math.ceil(len(keys) / 20)):
        temp.append(",".join(keys[i * 20:(i + 1) * 20]))
    return temp


def publish_sing_text(uuid, id, data, home_team, away_team, user):
    """
    给目标用户 发布单条text
    :param uuid: 标记比赛的uuid
    :param data: 单条text json数据
    :param id: 单条text的id
    :param home_team_name:
    :param away_team_name:
    :param user: {"username": "", "password": "", "tag_team": ""}
    :return:
    """
    # 单条图文文本的发布
    if home_team == user["tag_team"] or away_team == user["tag_team"]:
        if data.get("plus") and data.get("plus").startswith("+"):
            match_res = re.search("\[.*?\]", data["content"]).group() if re.search("\[.*?\]", data["content"]) else "[]"
            team_name = match_res[1:-1].split(" ")
            if team_name[0] == user["tag_team"]:  # 是目标队得分
                cache_text = redis_conn.get(id)
                if not cache_text:  # text无缓存
                    cache_time_node_res = redis_conn.get(user["username"] + "_time_node_" + uuid)
                    cache_time_node = cache_time_node_res.decode() if cache_time_node_res else ""
                    now_time = datetime.datetime.now()
                    if not cache_time_node or (now_time - datetime.timedelta(minutes=constants.TIME_LAG)).strftime(
                            "%Y-%m-%d %H:%M:%S") > cache_time_node:
                        # 发送
                        publish_text.delay(user["username"], user["password"], data["content"])
                        # 缓存时间 缓存text
                        redis_conn.setex(user["username"] + "_time_node_" + uuid, constants.TIME_NODE_EXPIRY, now_time.strftime("%Y-%m-%d %H:%M:%S"))
                        redis_conn.setex(id, constants.TEXT_EXPIRY, data["content"])  # 将发送的text缓存24小时
                        print("单条发送函数执行...")


def publish_text_to_tag_team(text, user, home_team, away_team):
    """
    给目标用户
    发送赛前text/赛后text
    :param text:
    :param user: {"username": "", "password": "", "tag_team": ""}
    :param home_team:
    :param away_team:
    :return:
    """
    if home_team == user["tag_team"] or away_team == user["tag_team"]:
        # 发送
        text = text.replace("<p>", "").replace("</p>", "\r\n")
        publish_text.delay(user["username"], user["password"], text)
        print("赛前text/赛后text发送函数执行...")
