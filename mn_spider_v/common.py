#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-12-7 下午2:19
# @Description: 公共函数
import hashlib
import math
import re

from mn_spider_v.clients import mysql_conn
from mn_spider_v.publish_content import TouTiaoLogin, TouTiaoPosted


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

    :param keys:
    :return:
    """
    # [",".join(keys[i * 20:(i + 1) * 20]) for i in range(0, math.ceil(len(keys) / 20))]
    temp = []
    for i in range(0, math.ceil(len(keys) / 20)):
        temp.append(",".join(keys[i * 20:(i + 1) * 20]))
    return temp


def nba_text_create(db, uuid):
    """
    生成nba推文
    :return:
    """
    # data = db["mn_sports_qq_nba_teletext"].find({"uuid": uuid})["data"]
    ids = db["mn_sports_qq_nba_teletext"].find_one({"_id": uuid})["data"]
    # print(ids)
    # 将字符串id转换为ObjectId对象
    # ids = list(map(ObjectId, ids))
    data = db["mn_sports_qq_nba_text"].find({"_id": {"$in": ids}})
    data = list(data)
    vs_score_dict = db["mn_sports_qq_nba_score"].find_one({"_id": uuid})["data"]
    vs_info_data = db["mn_sports_qq_nba_vs"].find_one({"_id": uuid})["data"]
    vs_pog_data = db["mn_sports_qq_nba_pog"].find_one({"_id": uuid})["data"]
    vs_count_data = db["mn_sports_qq_nba_count"].find_one({"_id": uuid})["data"]

    text = "<p>"
    # 遍历拼接
    for teletext in data:
        if not teletext.get("quarter"):
            text += teletext["content"]
            if data[data.index(teletext) + 1].get("quarter") == "第1节":  # 首段結束
                text += "<p>比赛开始，"

        elif teletext.get("quarter") == "第1节":
            if teletext.get("plus") and teletext.get("plus").startswith("+"):
                # 提取得分时推送信息
                match_obj = re.search(r"].*?（", teletext["content"], re.S)
                res_search = match_obj.group()
                re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                text += re_sub + "；"
            if teletext.get("content") == "本节比赛结束":
                # 第一节末比分比较
                home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分
                score_h = home_team_score_dict["st1"] if int(home_team_score_dict["st1"]) > int(
                    away_team_score_dict["st1"]) else away_team_score_dict["st1"]
                score_l = home_team_score_dict["st1"] if int(home_team_score_dict["st1"]) < int(
                    away_team_score_dict["st1"]) else away_team_score_dict["st1"]

                if int(score_h) == int(score_l):
                    text += vs_score_dict["home_team"]["name"] + score_h + "-" + score_l + "与" + vs_score_dict[
                        "away_team"]["name"] + "打平。</p>"
                    text += "<p>第二节，"
                else:
                    score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["st1"]) > int(
                        away_team_score_dict["st1"]) else vs_score_dict["away_team"]["name"]
                    score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["st1"]) < int(
                        away_team_score_dict["st1"]) else vs_score_dict["away_team"]["name"]
                    text += score_h_team + score_h + "-" + score_l + "领先" + score_l_team + "。</p>"
                    text += "<p>第二节，"

        elif teletext.get("quarter") == "第2节":
            if teletext.get("plus") and teletext.get("plus").startswith("+"):
                # 提取得分时推送信息
                # print(teletext["content"])
                match_obj = re.search(r"].*?（", teletext["content"], re.S)
                # print(match_obj)
                if not match_obj:
                    continue
                res_search = match_obj.group()
                re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                text += re_sub + "；"
            if teletext.get("content") == "本节比赛结束":
                # 第二节末比分比较
                home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分
                score_h = home_team_score_dict["nd2"] if int(home_team_score_dict["nd2"]) > int(
                    away_team_score_dict["nd2"]) else away_team_score_dict["nd2"]
                score_l = home_team_score_dict["nd2"] if int(home_team_score_dict["nd2"]) < int(
                    away_team_score_dict["nd2"]) else away_team_score_dict["nd2"]
                if int(score_h) == int(score_l):
                    text += vs_score_dict["home_team"]["name"] + score_h + "-" + score_l + "与" + vs_score_dict[
                        "away_team"]["name"] + "打平。</p>"
                    text += "<p>易边再战，"
                else:
                    score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["nd2"]) > int(
                        away_team_score_dict["nd2"]) else vs_score_dict["away_team"]["name"]
                    score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["nd2"]) < int(
                        away_team_score_dict["nd2"]) else vs_score_dict["away_team"]["name"]
                    text += score_h_team + score_h + "-" + score_l + "领先" + score_l_team + "。</p>"
                    text += "<p>易边再战，"

        elif teletext.get("quarter") == "第3节":
            if teletext.get("plus") and teletext.get("plus").startswith("+"):
                # 提取得分时推送信息
                match_obj = re.search(r"].*?（", teletext["content"], re.S)
                res_search = match_obj.group()
                re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                text += re_sub + "；"
            if teletext.get("content") == "本节比赛结束":
                # 第三节末比分比较
                home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分
                score_h = home_team_score_dict["rd3"] if int(home_team_score_dict["rd3"]) > int(
                    away_team_score_dict["rd3"]) else away_team_score_dict["rd3"]
                score_l = home_team_score_dict["rd3"] if int(home_team_score_dict["rd3"]) < int(
                    away_team_score_dict["rd3"]) else away_team_score_dict["rd3"]
                if int(score_h) == int(score_l):
                    text += vs_score_dict["home_team"]["name"] + score_h + "-" + score_l + "与" + vs_score_dict[
                        "away_team"]["name"] + "打平。</p>"
                    text += "<p>第四节，"
                else:
                    score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["rd3"]) > int(
                        away_team_score_dict["rd3"]) else vs_score_dict["away_team"]["name"]
                    score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["rd3"]) < int(
                        away_team_score_dict["rd3"]) else vs_score_dict["away_team"]["name"]
                    text += score_h_team + score_h + "-" + score_l + "领先" + score_l_team + "。</p>"
                    text += "<p>第四节，"

        elif teletext.get("quarter") == "第4节":
            if teletext.get("plus") and teletext.get("plus").startswith("+"):
                # 提取得分时推送信息
                match_obj = re.search(r"].*?（", teletext["content"], re.S)
                res_search = match_obj.group()
                re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                text += re_sub + "；"

            if teletext.get("content") == "本节比赛结束":
                # 第四场末比较总分
                home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分

                if len(home_team_score_dict.keys()) > 6:  # 进入加时赛
                    # print(home_team_score_dict.values())
                    # home_team_count = sum(map(int, home_team_score_dict.values()[1:5]))  # 前四场总分
                    home_team_count = int(home_team_score_dict["st1"]) + int(home_team_score_dict["nd2"]) + int(
                        home_team_score_dict["rd3"]) + int(home_team_score_dict["th4"])
                    text += vs_score_dict["home_team"]["name"] + str(home_team_count) + "-" + str(
                        home_team_count) + "与" + \
                            vs_score_dict[
                                "away_team"]["name"] + "打平，进入加时赛。</p>"
                else:
                    score_h = home_team_score_dict["count"] if int(home_team_score_dict["count"]) > int(
                        away_team_score_dict["count"]) else away_team_score_dict["count"]
                    score_l = home_team_score_dict["count"] if int(home_team_score_dict["count"]) < int(
                        away_team_score_dict["count"]) else away_team_score_dict["count"]
                    score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["count"]) > int(
                        away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                    score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["count"]) < int(
                        away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                    text += score_h_team + score_h + "-" + score_l + "战胜" + score_l_team + "。</p>"
        else:  # 加时赛
            # 从vs_score_dict判断有几场加时赛
            # 遍历场次
            if len(vs_score_dict["home_team"].keys()) > 6:
                # print(vs_score_dict["home_team"].keys())
                # print(vs_score_dict["home_team"].values())
                # ot_list = vs_score_dict["home_team"][5:-1]
                ot_item_list = [(ot_key, ot_value) for ot_key, ot_value in vs_score_dict["home_team"].items() if
                                ot_key.startswith("ot")]
                ot_item_dict = dict(ot_item_list)  # ot1、ot2、ot3...这种规律性的键会默认排序
                # ot_key_list = ot_item_dict.keys()
                ot_list = list(ot_item_dict.values())
                for ot in ot_list:
                    if teletext.get("quarter") == "加时" + str(ot_list.index(ot) + 1):
                        if teletext.get("plus") and teletext.get("plus").startswith("+"):
                            # 提取得分时推送信息
                            match_obj = re.search(r"].*?（", teletext["content"], re.S)
                            res_search = match_obj.group()
                            re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                            text += re_sub + "；"
                        if teletext.get("content") == "本节比赛结束":
                            # 加时赛末
                            home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                            away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分

                            if ot_list.index(ot) < len(ot_list) - 1:  # 进入加时赛
                                # home_team_count = sum(map(int, home_team_score_dict.values()[1:ot_list.index(ot) + 6]))  # 前4+ot(n)场总分
                                ot_count = sum(map(int, ot_list[0:ot_list.index(ot) + 1]))  # 加时赛得分
                                home_team_count = int(home_team_score_dict["st1"]) + int(
                                    home_team_score_dict["nd2"]) + int(home_team_score_dict["rd3"]) + int(
                                    home_team_score_dict["th4"]) + ot_count
                                text += vs_score_dict["home_team"]["name"] + str(home_team_count) + "-" + str(
                                    home_team_count) + "与" + \
                                        vs_score_dict[
                                            "away_team"]["name"] + "打平，进入加时赛。</p>"
                            else:
                                score_h = home_team_score_dict["count"] if int(home_team_score_dict["count"]) > int(
                                    away_team_score_dict["count"]) else away_team_score_dict["count"]
                                score_l = home_team_score_dict["count"] if int(home_team_score_dict["count"]) < int(
                                    away_team_score_dict["count"]) else away_team_score_dict["count"]
                                score_h_team = vs_score_dict["home_team"]["name"] if int(
                                    home_team_score_dict["count"]) > int(
                                    away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                                score_l_team = vs_score_dict["home_team"]["name"] if int(
                                    home_team_score_dict["count"]) < int(
                                    away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                                text += score_h_team + score_h + "-" + score_l + "战胜" + score_l_team + "。</p>"

    # 末尾段
    text += "<p>全场比赛，"
    match_best = {}
    team_best = {}
    temp_text = ""
    # for keys, values in vs_pog_data:
    if vs_pog_data["home_team"]["goal"]["num"] > vs_pog_data["away_team"]["goal"]["num"]:
        match_best_name = vs_pog_data["home_team"]["goal"]["name"]
        team_best_name = vs_pog_data["away_team"]["goal"]["name"]
        if not match_best.get(match_best_name):
            match_best[match_best_name] = ["goal"]
        else:
            match_best[match_best_name].append("goal")
        if not team_best.get(team_best_name):
            team_best[team_best_name] = ["goal"]
        else:
            team_best[team_best_name].append("goal")
    else:
        match_best_name = vs_pog_data["away_team"]["goal"]["name"]
        team_best_name = vs_pog_data["home_team"]["goal"]["name"]
        if not match_best.get(match_best_name):
            match_best[match_best_name] = ["goal"]
        else:
            match_best[match_best_name].append("goal")
        if not team_best.get(team_best_name):
            team_best[team_best_name] = ["goal"]
        else:
            team_best[team_best_name].append("goal")

    if vs_pog_data["home_team"]["assist"]["num"] > vs_pog_data["away_team"]["assist"]["num"]:
        match_best_name = vs_pog_data["home_team"]["assist"]["name"]
        team_best_name = vs_pog_data["away_team"]["assist"]["name"]
        if not match_best.get(match_best_name):
            match_best[match_best_name] = ["assist"]
        else:
            match_best[match_best_name].append("assist")
        if not team_best.get(team_best_name):
            team_best[team_best_name] = ["assist"]
        else:
            team_best[team_best_name].append("assist")
    else:
        match_best_name = vs_pog_data["away_team"]["assist"]["name"]
        team_best_name = vs_pog_data["home_team"]["assist"]["name"]
        if not match_best.get(match_best_name):
            match_best[match_best_name] = ["assist"]
        else:
            match_best[match_best_name].append("assist")
        if not team_best.get(team_best_name):
            team_best[team_best_name] = ["assist"]
        else:
            team_best[team_best_name].append("assist")

    if vs_pog_data["home_team"]["backboard"]["num"] > vs_pog_data["away_team"]["backboard"]["num"]:
        match_best_name = vs_pog_data["home_team"]["backboard"]["name"]
        team_best_name = vs_pog_data["away_team"]["backboard"]["name"]
        if not match_best.get(match_best_name):
            match_best[match_best_name] = ["backboard"]
        else:
            match_best[match_best_name].append("backboard")
        if not team_best.get(team_best_name):
            team_best[team_best_name] = ["backboard"]
        else:
            team_best[team_best_name].append("backboard")
    else:
        match_best_name = vs_pog_data["away_team"]["backboard"]["name"]
        team_best_name = vs_pog_data["home_team"]["backboard"]["name"]
        if not match_best.get(match_best_name):
            match_best[match_best_name] = ["backboard"]
        else:
            match_best[match_best_name].append("backboard")
        if not team_best.get(team_best_name):
            team_best[team_best_name] = ["backboard"]
        else:
            team_best[team_best_name].append("backboard")

    dict_temp = {"goal": "分", "assist": "助攻", "backboard": "篮板"}
    for name, pog in match_best.items():  # 全场最佳
        if len(pog) == 1:  # 只拿单项最值
            val = pog[0]
            if vs_pog_data["home_team"][val]["name"] == name:
                temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                    "name"] + "拿下全场最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + "；"
            else:
                temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                    "name"] + "拿下全场最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + "；"
        else:  # 拿了多项最值
            for val in pog:
                if vs_pog_data["home_team"][val]["name"] == name:
                    if pog.index(val) == 0:
                        temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                            "name"]
                    if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                        temp_text += "；"
                    temp_text += "拿下全场最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + ","
                else:
                    if pog.index(val) == 0:
                        temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                            "name"]
                    if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                        temp_text += "；"
                    temp_text += "拿下全场最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + ","

    for name, pog in team_best.items():  # 全队最佳
        if len(pog) == 1:
            val = pog[0]
            if vs_pog_data["home_team"][val]["name"] == name:
                temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                    "name"] + "拿下全队最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + "；"
            else:
                temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                    "name"] + "拿下全队最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + "；"
        else:
            for val in pog:
                if vs_pog_data["home_team"][val]["name"] == name:
                    if pog.index(val) == 0:
                        temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                            "name"]
                    if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                        temp_text += "；"
                    temp_text += "拿下全队最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + "，"
                else:
                    if pog.index(val) == 0:
                        temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                            "name"]
                    if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                        temp_text += "；"
                    temp_text += "拿下全队最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + "，"

    text += temp_text[0:-1] + "。</p>"
    # queue.put(text)
    return text


def nba_text_after(db, uuid):
    """
    赛后总结生成
    ps： 第一段取首发前的每第一句
    :param db:
    :param uuid:
    :return:
    """
    # data = db["mn_sports_qq_nba_teletext"].find({"uuid": uuid})["data"]
    ids = db["mn_sports_qq_nba_teletext"].find_one({"_id": uuid})["data"]
    # print(ids)
    # 将字符串id转换为ObjectId对象
    # ids = list(map(ObjectId, ids))
    data = db["mn_sports_qq_nba_text"].find({"_id": {"$in": ids}})
    vs_score = db["mn_sports_qq_nba_score"].find_one({"_id": uuid})
    # vs_info_data = db["mn_sports_qq_nba_vs"].find_one({"_id": uuid})["data"]
    vs_pog = db["mn_sports_qq_nba_pog"].find_one({"_id": uuid})
    # vs_count_data = db["mn_sports_qq_nba_count"].find_one({"_id": uuid})["data"]

    text = ""
    if all([data, vs_score, vs_pog]):
        vs_score_dict = vs_score["data"]
        vs_pog_data = vs_pog["data"]
        data = sorted(data, key=lambda x: x["data"]["sendTime"])
        text += "<p>"
        # 遍历拼接
        for teletext in data:
            if not teletext["data"].get("quarter"):     # 赛前推送
                if teletext["data"].get("content"):
                    if "届时" in teletext["data"].get("content") or "将" in teletext["data"].get("content") or "敬请期待" in teletext["data"].get(
                            "content") or "明天" in teletext["data"].get("content"):
                        continue
                    if "前瞻" in teletext["data"].get("content") or "首发" in teletext["data"].get("content") or "先发" in teletext["data"].get(
                            "content"):
                        continue
                    # 拼接每条赛前推送的第一句
                    text += teletext["data"].get("content").split("。")[0]
                if len(data) > data.index(teletext) + 1:
                    if data[data.index(teletext) + 1]["data"].get("quarter") == "第1节":  # 首段結束
                        text += "<p>比赛开始，"

            elif teletext["data"].get("quarter") == "第1节":
                if teletext["data"].get("plus") and teletext["data"].get("plus").startswith("+"):
                    # 提取得分时推送信息
                    match_obj = re.search(r"].*?（", teletext["data"]["content"], re.S)
                    res_search = match_obj.group()
                    re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                    text += re_sub + "；"
                if teletext["data"].get("content") == "本节比赛结束":
                    # 第一节末比分比较
                    home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                    away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分
                    score_h = home_team_score_dict["st1"] if int(home_team_score_dict["st1"]) > int(
                        away_team_score_dict["st1"]) else away_team_score_dict["st1"]
                    score_l = home_team_score_dict["st1"] if int(home_team_score_dict["st1"]) < int(
                        away_team_score_dict["st1"]) else away_team_score_dict["st1"]

                    if int(score_h) == int(score_l):
                        text += vs_score_dict["home_team"]["name"] + score_h + "-" + score_l + "与" + vs_score_dict[
                            "away_team"]["name"] + "打平。</p>"
                        text += "<p>第二节，"
                    else:
                        score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["st1"]) > int(
                            away_team_score_dict["st1"]) else vs_score_dict["away_team"]["name"]
                        score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["st1"]) < int(
                            away_team_score_dict["st1"]) else vs_score_dict["away_team"]["name"]
                        text += score_h_team + score_h + "-" + score_l + "领先" + score_l_team + "。</p>"
                        text += "<p>第二节，"

            elif teletext["data"].get("quarter") == "第2节":
                if teletext["data"].get("plus") and teletext["data"].get("plus").startswith("+"):
                    # 提取得分时推送信息
                    # print(teletext["content"])
                    match_obj = re.search(r"].*?（", teletext["data"]["content"], re.S)
                    # print(match_obj)
                    if not match_obj:
                        continue
                    res_search = match_obj.group()
                    re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                    text += re_sub + "；"
                if teletext["data"].get("content") == "本节比赛结束":
                    # 第二节末比分比较
                    home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                    away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分
                    score_h = home_team_score_dict["nd2"] if int(home_team_score_dict["nd2"]) > int(
                        away_team_score_dict["nd2"]) else away_team_score_dict["nd2"]
                    score_l = home_team_score_dict["nd2"] if int(home_team_score_dict["nd2"]) < int(
                        away_team_score_dict["nd2"]) else away_team_score_dict["nd2"]
                    if int(score_h) == int(score_l):
                        text += vs_score_dict["home_team"]["name"] + score_h + "-" + score_l + "与" + vs_score_dict[
                            "away_team"]["name"] + "打平。</p>"
                        text += "<p>易边再战，"
                    else:
                        score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["nd2"]) > int(
                            away_team_score_dict["nd2"]) else vs_score_dict["away_team"]["name"]
                        score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["nd2"]) < int(
                            away_team_score_dict["nd2"]) else vs_score_dict["away_team"]["name"]
                        text += score_h_team + score_h + "-" + score_l + "领先" + score_l_team + "。</p>"
                        text += "<p>易边再战，"

            elif teletext["data"].get("quarter") == "第3节":
                if teletext["data"].get("plus") and teletext["data"].get("plus").startswith("+"):
                    # 提取得分时推送信息
                    match_obj = re.search(r"].*?（", teletext["data"]["content"], re.S)
                    res_search = match_obj.group()
                    re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                    text += re_sub + "；"
                if teletext["data"].get("content") == "本节比赛结束":
                    # 第三节末比分比较
                    home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                    away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分
                    score_h = home_team_score_dict["rd3"] if int(home_team_score_dict["rd3"]) > int(
                        away_team_score_dict["rd3"]) else away_team_score_dict["rd3"]
                    score_l = home_team_score_dict["rd3"] if int(home_team_score_dict["rd3"]) < int(
                        away_team_score_dict["rd3"]) else away_team_score_dict["rd3"]
                    if int(score_h) == int(score_l):
                        text += vs_score_dict["home_team"]["name"] + score_h + "-" + score_l + "与" + vs_score_dict[
                            "away_team"]["name"] + "打平。</p>"
                        text += "<p>第四节，"
                    else:
                        score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["rd3"]) > int(
                            away_team_score_dict["rd3"]) else vs_score_dict["away_team"]["name"]
                        score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["rd3"]) < int(
                            away_team_score_dict["rd3"]) else vs_score_dict["away_team"]["name"]
                        text += score_h_team + score_h + "-" + score_l + "领先" + score_l_team + "。</p>"
                        text += "<p>第四节，"

            elif teletext["data"].get("quarter") == "第4节":
                if teletext["data"].get("plus") and teletext["data"].get("plus").startswith("+"):
                    # 提取得分时推送信息
                    match_obj = re.search(r"].*?（", teletext["data"]["content"], re.S)
                    res_search = match_obj.group()
                    re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                    text += re_sub + "；"

                if teletext["data"].get("content") == "本节比赛结束":
                    # 第四场末比较总分
                    home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                    away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分

                    if len(home_team_score_dict.keys()) > 6:  # 进入加时赛
                        # print(home_team_score_dict.values())
                        # home_team_count = sum(map(int, home_team_score_dict.values()[1:5]))  # 前四场总分
                        home_team_count = int(home_team_score_dict["st1"]) + int(home_team_score_dict["nd2"]) + int(
                            home_team_score_dict["rd3"]) + int(home_team_score_dict["th4"])
                        text += vs_score_dict["home_team"]["name"] + str(home_team_count) + "-" + str(
                            home_team_count) + "与" + \
                                vs_score_dict[
                                    "away_team"]["name"] + "打平，进入加时赛。</p>"
                    else:
                        score_h = home_team_score_dict["count"] if int(home_team_score_dict["count"]) > int(
                            away_team_score_dict["count"]) else away_team_score_dict["count"]
                        score_l = home_team_score_dict["count"] if int(home_team_score_dict["count"]) < int(
                            away_team_score_dict["count"]) else away_team_score_dict["count"]
                        score_h_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["count"]) > int(
                            away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                        score_l_team = vs_score_dict["home_team"]["name"] if int(home_team_score_dict["count"]) < int(
                            away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                        text += score_h_team + score_h + "-" + score_l + "战胜" + score_l_team + "。</p>"
            else:  # 加时赛
                # 从vs_score_dict判断有几场加时赛
                # 遍历场次
                if len(vs_score_dict["home_team"].keys()) > 6:
                    # print(vs_score_dict["home_team"].keys())
                    # print(vs_score_dict["home_team"].values())
                    # ot_list = vs_score_dict["home_team"][5:-1]
                    ot_item_list = [(ot_key, ot_value) for ot_key, ot_value in vs_score_dict["home_team"].items() if
                                    ot_key.startswith("ot")]
                    ot_item_dict = dict(ot_item_list)  # ot1、ot2、ot3...这种规律性的键会默认排序
                    # ot_key_list = ot_item_dict.keys()
                    ot_list = list(ot_item_dict.values())
                    for ot in ot_list:
                        if teletext["data"].get("quarter") == "加时" + str(ot_list.index(ot) + 1):
                            if teletext["data"].get("plus") and teletext["data"].get("plus").startswith("+"):
                                # 提取得分时推送信息
                                match_obj = re.search(r"].*?（", teletext["data"]["content"], re.S)
                                res_search = match_obj.group()
                                re_sub = re.sub(r"[^\u4e00-\u9fa5]*", "", res_search)
                                text += re_sub + "；"
                            if teletext.get("content") == "本节比赛结束":
                                # 加时赛末
                                home_team_score_dict = vs_score_dict["home_team"]  # 主队本场所有小节得分
                                away_team_score_dict = vs_score_dict["away_team"]  # 客队本场所有小节得分

                                if ot_list.index(ot) < len(ot_list) - 1:  # 进入加时赛
                                    # home_team_count = sum(map(int, home_team_score_dict.values()[1:ot_list.index(ot) + 6]))  # 前4+ot(n)场总分
                                    ot_count = sum(map(int, ot_list[0:ot_list.index(ot) + 1]))  # 加时赛得分
                                    home_team_count = int(home_team_score_dict["st1"]) + int(
                                        home_team_score_dict["nd2"]) + int(home_team_score_dict["rd3"]) + int(
                                        home_team_score_dict["th4"]) + ot_count
                                    text += vs_score_dict["home_team"]["name"] + str(home_team_count) + "-" + str(
                                        home_team_count) + "与" + \
                                            vs_score_dict[
                                                "away_team"]["name"] + "打平，进入加时赛。</p>"
                                else:
                                    score_h = home_team_score_dict["count"] if int(home_team_score_dict["count"]) > int(
                                        away_team_score_dict["count"]) else away_team_score_dict["count"]
                                    score_l = home_team_score_dict["count"] if int(home_team_score_dict["count"]) < int(
                                        away_team_score_dict["count"]) else away_team_score_dict["count"]
                                    score_h_team = vs_score_dict["home_team"]["name"] if int(
                                        home_team_score_dict["count"]) > int(
                                        away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                                    score_l_team = vs_score_dict["home_team"]["name"] if int(
                                        home_team_score_dict["count"]) < int(
                                        away_team_score_dict["count"]) else vs_score_dict["away_team"]["name"]
                                    text += score_h_team + score_h + "-" + score_l + "战胜" + score_l_team + "。</p>"

        # 末尾段
        text += "<p>全场比赛，"
        match_best = {}
        team_best = {}
        temp_text = ""
        # for keys, values in vs_pog_data:
        if vs_pog_data["home_team"]["goal"]["num"] > vs_pog_data["away_team"]["goal"]["num"]:
            match_best_name = vs_pog_data["home_team"]["goal"]["name"]
            team_best_name = vs_pog_data["away_team"]["goal"]["name"]
            if not match_best.get(match_best_name):
                match_best[match_best_name] = ["goal"]
            else:
                match_best[match_best_name].append("goal")
            if not team_best.get(team_best_name):
                team_best[team_best_name] = ["goal"]
            else:
                team_best[team_best_name].append("goal")
        else:
            match_best_name = vs_pog_data["away_team"]["goal"]["name"]
            team_best_name = vs_pog_data["home_team"]["goal"]["name"]
            if not match_best.get(match_best_name):
                match_best[match_best_name] = ["goal"]
            else:
                match_best[match_best_name].append("goal")
            if not team_best.get(team_best_name):
                team_best[team_best_name] = ["goal"]
            else:
                team_best[team_best_name].append("goal")

        if vs_pog_data["home_team"]["assist"]["num"] > vs_pog_data["away_team"]["assist"]["num"]:
            match_best_name = vs_pog_data["home_team"]["assist"]["name"]
            team_best_name = vs_pog_data["away_team"]["assist"]["name"]
            if not match_best.get(match_best_name):
                match_best[match_best_name] = ["assist"]
            else:
                match_best[match_best_name].append("assist")
            if not team_best.get(team_best_name):
                team_best[team_best_name] = ["assist"]
            else:
                team_best[team_best_name].append("assist")
        else:
            match_best_name = vs_pog_data["away_team"]["assist"]["name"]
            team_best_name = vs_pog_data["home_team"]["assist"]["name"]
            if not match_best.get(match_best_name):
                match_best[match_best_name] = ["assist"]
            else:
                match_best[match_best_name].append("assist")
            if not team_best.get(team_best_name):
                team_best[team_best_name] = ["assist"]
            else:
                team_best[team_best_name].append("assist")

        if vs_pog_data["home_team"]["backboard"]["num"] > vs_pog_data["away_team"]["backboard"]["num"]:
            match_best_name = vs_pog_data["home_team"]["backboard"]["name"]
            team_best_name = vs_pog_data["away_team"]["backboard"]["name"]
            if not match_best.get(match_best_name):
                match_best[match_best_name] = ["backboard"]
            else:
                match_best[match_best_name].append("backboard")
            if not team_best.get(team_best_name):
                team_best[team_best_name] = ["backboard"]
            else:
                team_best[team_best_name].append("backboard")
        else:
            match_best_name = vs_pog_data["away_team"]["backboard"]["name"]
            team_best_name = vs_pog_data["home_team"]["backboard"]["name"]
            if not match_best.get(match_best_name):
                match_best[match_best_name] = ["backboard"]
            else:
                match_best[match_best_name].append("backboard")
            if not team_best.get(team_best_name):
                team_best[team_best_name] = ["backboard"]
            else:
                team_best[team_best_name].append("backboard")

        dict_temp = {"goal": "分", "assist": "助攻", "backboard": "篮板"}
        for name, pog in match_best.items():  # 全场最佳
            if len(pog) == 1:  # 只拿单项最值
                val = pog[0]
                if vs_pog_data["home_team"][val]["name"] == name:
                    temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                        "name"] + "拿下全场最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + "；"
                else:
                    temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                        "name"] + "拿下全场最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + "；"
            else:  # 拿了多项最值
                for val in pog:
                    if vs_pog_data["home_team"][val]["name"] == name:
                        if pog.index(val) == 0:
                            temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                                "name"]
                        if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                            temp_text += "；"
                        temp_text += "拿下全场最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + ","
                    else:
                        if pog.index(val) == 0:
                            temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                                "name"]
                        if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                            temp_text += "；"
                        temp_text += "拿下全场最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + ","

        for name, pog in team_best.items():  # 全队最佳
            if len(pog) == 1:
                val = pog[0]
                if vs_pog_data["home_team"][val]["name"] == name:
                    temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                        "name"] + "拿下全队最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + "；"
                else:
                    temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                        "name"] + "拿下全队最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + "；"
            else:
                for val in pog:
                    if vs_pog_data["home_team"][val]["name"] == name:
                        if pog.index(val) == 0:
                            temp_text += vs_pog_data["home_team"]["team_name"] + "队" + vs_pog_data["home_team"][val][
                                "name"]
                        if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                            temp_text += "；"
                        temp_text += "拿下全队最高" + vs_pog_data["home_team"][val]["num"] + dict_temp[val] + "，"
                    else:
                        if pog.index(val) == 0:
                            temp_text += vs_pog_data["away_team"]["team_name"] + "队" + vs_pog_data["away_team"][val][
                                "name"]
                        if pog.index(val) != 0 and pog.index(val) == len(pog) - 1:
                            temp_text += "；"
                        temp_text += "拿下全队最高" + vs_pog_data["away_team"][val]["num"] + dict_temp[val] + "，"

        text += temp_text[0:-1] + "。</p>"
        # queue.put(text)
    return text


def nba_text_before(db, uuid):
    """
    赛前文本生成
    :param db:
    :param uuid:
    :return:
    """
    ids = db["mn_sports_qq_nba_teletext"].find_one({"_id": uuid})["data"]
    # print(ids)
    # 将字符串id转换为ObjectId对象
    # ids = list(map(ObjectId, ids))
    data = db["mn_sports_qq_nba_text"].find({"_id": {"$in": ids}})
    data = list(data)
    # print(data)
    if data:
        text = ""
        # 遍历拼接
        for teletext in data:
            if not teletext["data"].get("quarter"):
                # pprint(teletext)
                if teletext["data"].get("content"):
                    if "前瞻" in teletext["data"].get("content") or "首发" in teletext["data"].get("content") or "先发" in teletext["data"].get(
                            "content"):
                        break
                    text += "<p>" + teletext["data"]["content"] + "</p>"
        return text


if __name__ == "__main__":
    # publish_content("18229854080", "Lzw1911@", "今天天气好晴朗，处处好风光！")
    from mn_spider_v.clients import mongo_conn
    from mn_spider_v import constants
    text = nba_text_after(mongo_conn[constants.DB], "f424c6bc9d8893627b39c67973365203")
    print(text)
