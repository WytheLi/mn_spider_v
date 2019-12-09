# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time

from celery_tasks.publish.tasks import publish_text
from mn_spider_v import constants
from mn_spider_v.clients import mongo_conn, mysql_conn
from mn_spider_v.common import gen_nba_vs_uuid, nba_text_after, nba_text_before, \
    save_text_before_game_to_mysql, save_text_after_game_to_mysql

"""
给多个spider指定对应的pipline：
1、利用spider.name做分支判断；
2、直接在spider里设置pipline(scrapy是1.1以上版本)
参考博客： https://blog.csdn.net/harry5508/article/details/86486777
"""


class NbaMidPipeline(object):
    def process_item(self, item, spider):
        """
        保存mid数据 {"_id": [uuid], "date": "2019-10-01", "data": {}}
        :param item:
        :param spider:
        :return:
        """
        # print(item)
        for date, value in item.items():
            for mid_dict in value:
                # print(mid_dict["leftName"], mid_dict["rightName"], mid_dict["startTime"])
                uuid = gen_nba_vs_uuid(mid_dict["leftName"], mid_dict["rightName"], mid_dict["startTime"])
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                res = mongo_conn[constants.DB]["mn_sports_qq_nba_mid"].find_one({"_id": uuid})
                if not res:
                    mongo_conn[constants.DB]["mn_sports_qq_nba_mid"].insert_one({"_id": uuid, "date": date, "data": mid_dict, "create_date": now_time})


class NbaVsInfoPipeline(object):
    def process_item(self, item, spider):
        """
        保存selenium解析主页的数据
        {"_id": [uuid], "data": [dict or list],
        "home_team_name": "", "away_team_name": "", "create_time": "", "update_time": ""}
        :param item:
        :param spider:
        :return:
        """
        # print(item)
        # print("接受到yield数据")
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if item["item"]["data"]:
            # 无则插入，有则更新覆盖
            res = mongo_conn[constants.DB][item["collection"]].find_one({"_id": item["item"]["_id"]})
            if res:
                mongo_conn[constants.DB][item["collection"]].update_one({"_id": res["_id"]}, {"$set": {"data": item["item"]["data"], "update_time": now_time}})
            else:
                # 当主页面任意一个集合都没有数据，且图文集合有数据时，生成赛前文本，并发送
                teletext = mongo_conn[constants.DB]["mn_sports_qq_nba_teletext"].find_one({"_id": item["item"]["_id"]})
                pog = mongo_conn[constants.DB]["mn_sports_qq_nba_pog"].find_one({"_id": item["item"]["_id"]})
                score = mongo_conn[constants.DB]["mn_sports_qq_nba_score"].find_one({"_id": item["item"]["_id"]})
                count = mongo_conn[constants.DB]["mn_sports_qq_nba_count"].find_one({"_id": item["item"]["_id"]})
                vs_info = mongo_conn[constants.DB]["mn_sports_qq_nba_vs"].find_one({"_id": item["item"]["_id"]})
                if not any([pog, score, count, vs_info]) and teletext:
                    with mysql_conn.cursor() as cursor:
                        select_text = """
                            select id from mn_sports_qq_nba_text_before_game where id = %(uuid)s
                        """
                        cursor.execute(select_text, {"uuid": item["item"]["_id"]})
                        text_before_game = cursor.fetchone()
                        if not text_before_game:
                            # 生成文本
                            text_before_game = nba_text_before(mongo_conn[constants.DB], item["item"]["_id"])
                            if text_before_game:
                                # 保存赛前文本到mysql
                                save_text_before_game_to_mysql(item["item"]["_id"], text_before_game, item["item"]["home_team_name"], item["item"]["away_team_name"], item["item"]["start_time"])
                                # 发送
                                text_before_game = text_before_game.replace("<p>", "").replace("</p>", "\r\n")
                                publish_text.delay(constants.TT_USERNAME, constants.TT_PASSWORD, text_before_game)
                item["item"]["create_time"] = now_time
                item["item"]["update_time"] = now_time
                mongo_conn[constants.DB][item["collection"]].insert_one(item["item"])


class NbaTextKeysPipeline(object):
    def process_item(self, item, spider):
        """
        保存text keys数据
        :param item:
        :param spider:
        :return:
        """
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 无则插入，有则pass
        res = mongo_conn[constants.DB]["mn_sports_qq_nba_text_keys"].find_one({"_id": item["_id"]})
        if not res:
            item["create_time"] = now_time
            mongo_conn[constants.DB]["mn_sports_qq_nba_text_keys"].insert_one(item)


class NbaTextPipeline(object):
    def process_item(self, item, spider):
        """
        保存图文数据, 文本的生成、发布
        1、赛前文本的发布
            - (条件判断) 当主页面任意一个集合都没有数据，且图文爬虫yield数据时，生成赛前文本，并发送
        2、赛后文本的发布
            - 当text文档content字段包含“全场比赛结束”时，生成赛后文本，并发送
        3、赛中赛况
            -
        :param item:
        :param spider:
        :return:
        """
        # mn_sports_qq_nba_teletext
        # mn_sports_qq_nba_text
        uuid = gen_nba_vs_uuid(item["home_team_name"], item["away_team_name"], item["start_time"])
        for id, data in item["data"].items():
            text_res = mongo_conn[constants.DB]["mn_sports_qq_nba_text"].find_one({"_id": id})
            teletext = mongo_conn[constants.DB]["mn_sports_qq_nba_teletext"].find_one({"_id": uuid})
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if not text_res:    # 文档在text集合中不存在，插入文档
                mongo_conn[constants.DB]["mn_sports_qq_nba_text"].insert_one({"_id": id, "data": data, "create_time": now_time})
                if teletext:    # 文档所属于比赛在teletext集合存在，进一步判断text文档_id值是否存在于teletext集合
                    if id not in teletext["data"]:
                        teletext["data"].append(id)
                        mongo_conn[constants.DB]["mn_sports_qq_nba_teletext"].update_one({"_id": uuid}, {"$set": {"data": teletext["data"], "update_time": now_time}})
                else:       # 文档所属于比赛在teletext集合不存在，插入文档
                    ids = [id]
                    mongo_conn[constants.DB]["mn_sports_qq_nba_teletext"].insert_one({"_id": uuid, "data": ids, "create_time": now_time, "update_time": now_time})
            else:   # 文档在text集合中存在，判断其_id值是否也存在于teletext集合
                if id not in teletext["data"]:  # 其_id值是否也存在于teletext集合，更新集合
                    teletext["data"].append(id)
                    mongo_conn[constants.DB]["mn_sports_qq_nba_teletext"].update_one({"_id": uuid}, {"$set": {"data": teletext["data"], "update_time": now_time}})
            # 当yield text文档content字段包含“全场比赛结束”时，生成赛后文本，并发送
            if data["content"].startswith("全场比赛结束"):
                with mysql_conn.cursor() as cursor:
                    select_text = """
                        select id from mn_sports_qq_nba_text_after_game where id = %(uuid)s
                    """
                    cursor.execute(select_text, {"uuid": uuid})
                    text_after_game = cursor.fetchone()
                    if not text_after_game:
                        # 生成文本
                        text_after_game = nba_text_after(mongo_conn[constants.DB], uuid)
                        if text_after_game:
                            # save to mysql
                            save_text_after_game_to_mysql(uuid, text_after_game, item["home_team_name"], item["away_team_name"], item["start_time"])
                            # 发送
                            text_after_game = text_after_game.replace("<p>", "").replace("</p>", "\r\n")
                            publish_text.delay(constants.TT_USERNAME, constants.TT_PASSWORD, text_after_game)

