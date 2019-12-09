# -*- coding: utf-8 -*-
import scrapy

from mn_spider_v import constants
from mn_spider_v.clients import mongo_conn
from mn_spider_v.common import gen_nba_vs_uuid


class NbaVsInfoSpider(scrapy.Spider):
    name = 'nba_vs_info'
    allowed_domains = ['sports.qq.com']
    # start_urls = ['http://sports.qq.com/']
    res = mongo_conn[constants.DB]["mn_sports_qq_nba_mid"].find(
        {"$and": [{"date": {"$gte": constants.START_TIME}}, {"date": {"$lte": constants.END_TIME}}]})
    # for mid in data:
    #     print(mid["list"])
    urls = []
    if res:
        for sing_dict in res:
            urls.append("https://sports.qq.com/kbsweb/game.htm?mid=%s&start_time=%s" % (sing_dict["data"]["mid"], sing_dict["data"]["startTime"]))
    start_urls = urls
    custom_settings = { # 指定管道
        "ITEM_PIPELINES": {'mn_spider_v.pipelines.NbaVsInfoPipeline': 301}
    }

    def parse(self, response):
        # print("Response URL:", response.url)
        # print(response.text)
        start_time = response.url.split("=")[-1].replace("%20", " ")
        # print(start_time)
        team_name_both = response.xpath('//div[@id="container"]/div[@id="head-box"]/div[contains(@class, "inner")]//text()').extract()
        # print(team_name_both)
        home_team_name = team_name_both[9].strip()
        away_team_name = team_name_both[20].strip()
        # 生成uuid
        uuid = gen_nba_vs_uuid(home_team_name, away_team_name, start_time)
        # print(uuid, home_team_name, away_team_name, start_time)
        # scrapy封装的xpath解析 extract_first()提取第一条；extract()提取所有，返回列表
        home_team_list = response.xpath('//div[@class="content-wrapper"]//div[@class="host-goals"]/span//text()').extract()
        away_team_list = response.xpath('//div[@class="content-wrapper"]//div[@class="guest-goals"]/span//text()').extract()
        # selenium封装的xpath解析
        # home_team_list = driver.find_elements_by_xpath('//div[@class="content-wrapper"]//div[@class="host-goals"]/span')
        # away_team_list = driver.find_elements_by_xpath(
        #     '//div[@class="content-wrapper"]//div[@class="guest-goals"]/span')

        # print(home_team_list)
        # print(away_team_list)
        if home_team_list and away_team_list:
            vs_score_data = {}  # 存储比分数据
            if len(home_team_list) == 6:  # 未加时
                home_team = {
                    "name": home_team_list[0].strip(),
                    "st1": home_team_list[1].strip(),
                    "nd2": home_team_list[2].strip(),
                    "rd3": home_team_list[3].strip(),
                    "th4": home_team_list[4].strip(),
                    "count": home_team_list[5].strip()
                }
            else:  # 加时赛
                ot_values = home_team_list[5:-1]
                ot_keys = ["ot" + str(i + 1) for i in range(len(ot_values))]
                home_team = {
                    "name": home_team_list[0].strip(),
                    "st1": home_team_list[1].strip(),
                    "nd2": home_team_list[2].strip(),
                    "rd3": home_team_list[3].strip(),
                    "th4": home_team_list[4].strip(),
                    "count": home_team_list[-1].strip()
                }
                for ot in ot_values:
                    home_team[ot_keys[ot_values.index(ot)]] = ot.strip()
            vs_score_data["home_team"] = home_team

            if len(away_team_list) == 6:
                away_team = {
                    "name": away_team_list[0].strip(),
                    "st1": away_team_list[1].strip(),
                    "nd2": away_team_list[2].strip(),
                    "rd3": away_team_list[3].strip(),
                    "th4": away_team_list[4].strip(),
                    "count": away_team_list[5].strip()
                }
            else:
                ot_values = away_team_list[5:-1]
                ot_keys = ["ot" + str(i + 1) for i in range(len(ot_values))]
                away_team = {
                    "name": away_team_list[0].strip(),
                    "st1": away_team_list[1].strip(),
                    "nd2": away_team_list[2].strip(),
                    "rd3": away_team_list[3].strip(),
                    "th4": away_team_list[4].strip(),
                    "count": away_team_list[-1].strip()
                }
                for ot in ot_values:
                    home_team[ot_keys[ot_values.index(ot)]] = ot.strip()
            vs_score_data["away_team"] = away_team
            # print(vs_score_data)
            yield {"item": {"_id": uuid, "data": vs_score_data, "home_team_name": home_team_name, "away_team_name": away_team_name, "start_time": start_time}, "collection": "mn_sports_qq_nba_score"}

            vs_result_data = {
                "home_team": home_team_list[0].strip(),
                "away_team": away_team_list[0].strip(),
                "competition_time": "",
                "win": home_team_list[0].strip() if int(home_team_list[-1].strip()) > int(away_team_list[-1].strip()) else
                away_team_list[0].strip(),
                "lose": home_team_list[0].strip() if int(home_team_list[-1].strip()) < int(away_team_list[-1].strip()) else
                away_team_list[0].strip(),
            }
            # print(vs_result_data)
            yield {"item": {"_id": uuid, "data": vs_result_data, "home_team_name": home_team_name, "away_team_name": away_team_name, "start_time": start_time}, "collection": "mn_sports_qq_nba_vs"}

        # 本场概况 --> 本场最佳
        # team_name_both = driver.find_elements_by_xpath(
        #     '//div[@class="content-wrapper"]//div[@class="logo-section"]//span[contains(@class, "team-name")]')
        # pog_goal_both = driver.find_element_by_xpath('//div[@class="content-wrapper"]//ul[@class="data-info"]/li[1]')
        # pog_assist_both = driver.find_element_by_xpath('//div[@class="content-wrapper"]//ul[@class="data-info"]/li[2]')
        # pog_backboard_both = driver.find_element_by_xpath(
        #     '//div[@class="content-wrapper"]//ul[@class="data-info"]/li[3]')

        # scrapy封装的xpath解析
        pog_goal_both = response.xpath('//div[@class="content-wrapper"]//ul[@class="data-info"]/li[1]//text()').extract()
        pog_assist_both = response.xpath('//div[@class="content-wrapper"]//ul[@class="data-info"]/li[2]//text()').extract()
        pog_backboard_both = response.xpath('//div[@class="content-wrapper"]//ul[@class="data-info"]/li[3]//text()').extract()
        print(pog_goal_both)
        print(pog_assist_both)
        print(pog_backboard_both)

        pog_data = {}  # 存储本场最佳数据
        # 主队最佳分数
        home_team_pog_goal_score = pog_goal_both[2]
        home_team_pog_goal_number_name = pog_goal_both[0].strip()
        home_team_pog_goal_name = home_team_pog_goal_number_name.split("-")[1] if len(home_team_pog_goal_number_name.split("-")) == 2 else home_team_pog_goal_number_name.split("-")[0]
        home_team_pog_goal_number = home_team_pog_goal_number_name.split("-")[0] if len(home_team_pog_goal_number_name.split("-")) == 2 else ""
        # 主队最佳助攻
        home_team_pog_assist_num = pog_assist_both[2]
        home_team_pog_assist_number_name = pog_assist_both[0].strip()
        home_team_pog_assist_name = home_team_pog_assist_number_name.split("-")[1] if len(home_team_pog_assist_number_name.split("-")) == 2 else home_team_pog_assist_number_name.split("-")[0]
        home_team_pog_assist_number = home_team_pog_assist_number_name.split("-")[0] if len(home_team_pog_assist_number_name.split("-")) == 2 else ""
        # 主队最佳篮板
        home_team_pog_backboard_num = pog_backboard_both[2]
        home_team_pog_backboard_number_name = pog_backboard_both[0].strip()
        home_team_pog_backboard_name = home_team_pog_backboard_number_name.split("-")[1] if len(
            home_team_pog_backboard_number_name.split("-")) == 2 else home_team_pog_backboard_number_name.split("-")[0]
        home_team_pog_backboard_number = home_team_pog_backboard_number_name.split("-")[0] if len(
            home_team_pog_backboard_number_name.split("-")) == 2 else ""
        # 客场最佳分数
        away_team_pog_goal_score = pog_goal_both[6]
        away_team_pog_goal_number_name = pog_goal_both[8].strip()
        away_team_pog_goal_name = away_team_pog_goal_number_name.split("-")[1] if len(away_team_pog_goal_number_name.split("-")) else away_team_pog_goal_number_name.split("-")[0]
        away_team_pog_goal_number = away_team_pog_goal_number_name.split("-")[0] if len(away_team_pog_goal_number_name.split("-")) else ""
        # 客场最佳助攻
        away_team_pog_assist_num = pog_assist_both[6]
        away_team_pog_assist_number_name = pog_assist_both[8].strip()
        away_team_pog_assist_name = away_team_pog_assist_number_name.split("-")[1] if len(away_team_pog_assist_number_name.split("-")) else away_team_pog_assist_number_name.split("-")[0]
        away_team_pog_assist_number = away_team_pog_assist_number_name.split("-")[0] if len(away_team_pog_assist_number_name.split("-")) else ""
        # 客场最佳篮板
        away_team_pog_backboard_num = pog_backboard_both[6]
        away_team_pog_backboard_number_name = pog_backboard_both[8].strip()
        away_team_pog_backboard_name = away_team_pog_backboard_number_name.split("-")[1] if len(away_team_pog_backboard_number_name.split("-")) else away_team_pog_backboard_number_name.split("-")[0]
        away_team_pog_backboard_number = away_team_pog_backboard_number_name.split("-")[0] if len(away_team_pog_backboard_number_name.split("-")) else ""

        home_team_pog = {
            "team_name": home_team_name,
            "goal": {"num": home_team_pog_goal_score, "name": home_team_pog_goal_name,
                     "number": home_team_pog_goal_number},
            "assist": {"num": home_team_pog_assist_num, "name": home_team_pog_assist_name,
                       "number": home_team_pog_assist_number},
            "backboard": {"num": home_team_pog_backboard_num, "name": home_team_pog_backboard_name,
                          "number": home_team_pog_backboard_number}
        }
        away_team_pog = {
            "team_name": away_team_name,
            "goal": {"num": away_team_pog_goal_score, "name": away_team_pog_goal_name,
                     "number": away_team_pog_goal_number},
            "assist": {"num": away_team_pog_assist_num, "name": away_team_pog_assist_name,
                       "number": away_team_pog_assist_number},
            "backboard": {"num": away_team_pog_backboard_num, "name": away_team_pog_backboard_name,
                          "number": away_team_pog_backboard_number}
        }
        pog_data["home_team"] = home_team_pog
        pog_data["away_team"] = away_team_pog
        # print(pog_data)
        # yield {"_id": uuid, "home_team_name": home_team_name, "away_team_name": away_team_name, "data": pog_data}, "mn_sports_qq_nba_pog"
        yield {"item": {"_id": uuid, "data": pog_data, "home_team_name": home_team_name, "away_team_name": away_team_name, "start_time": start_time}, "collection": "mn_sports_qq_nba_pog"}

        # 技术统计数据解析
        count_data = []
        # tab_list = driver.find_elements_by_xpath(
        #     '//div[@class="tab-content"]//div[@class="skill-content"]//div[contains(@class, "content-row")]')
        tab_list = response.xpath('//div[@class="tab-content"]//div[@class="skill-content"]//div[contains(@class, "content-row")]')
        # print(tab_list)
        for row in tab_list:
            # span_list = row.find_elements_by_xpath('./div[contains(@class, "content-col")]//span')
            span_list = row.xpath('./div[contains(@class, "content-col")]//span//text()').extract()
            # print(span_list)
            if span_list[1].strip() == "统计":  # 多余统计行
                continue
            if len(span_list) == 15:
                temp_dict = {
                    "number": span_list[0].strip(),
                    "name": span_list[1].strip(),
                    "role": span_list[2].strip(),
                    "online_duration": span_list[3].strip(),
                    "score": span_list[4].strip(),
                    "backboard": span_list[5].strip(),
                    "assist": span_list[6].strip(),
                    "fgpbase_total": span_list[7].strip().split("/")[1],
                    "fgpbase_goal": span_list[7].strip().split("/")[0],
                    "threeptbas_total": span_list[8].strip().split("/")[1],
                    "threeptbas_goal": span_list[8].strip().split("/")[0],
                    "fta": span_list[9].strip().split("/")[1],
                    "ftm": span_list[9].strip().split("/")[0],
                    "steal": span_list[10].strip(),
                    "block_shot": span_list[11].strip(),
                    "turnover": span_list[12].strip(),
                    "foul": span_list[13].strip(),
                    "record": span_list[14].strip(),
                }
                count_data.append(temp_dict)
            else:
                temp_dict = {
                    "number": span_list[0].strip(),
                    "name": span_list[1].strip(),
                    "role": "",
                    "online_duration": span_list[2].strip(),
                    "score": span_list[3].strip(),
                    "backboard": span_list[4].strip(),
                    "assist": span_list[5].strip(),
                    "fgpbase_total": span_list[6].strip().split("/")[1],
                    "fgpbase_goal": span_list[6].strip().split("/")[0],
                    "threeptbas_total": span_list[7].strip().split("/")[1],
                    "threeptbas_goal": span_list[7].strip().split("/")[0],
                    "fta": span_list[8].strip().split("/")[1],
                    "ftm": span_list[8].strip().split("/")[0],
                    "steal": span_list[9].strip(),
                    "block_shot": span_list[10].strip(),
                    "turnover": span_list[11].strip(),
                    "foul": span_list[12].strip(),
                    "record": span_list[13].strip(),
                }
                count_data.append(temp_dict)
        # yield {"_id": uuid, "home_team_name": home_team_name, "away_team_name": away_team_name, "data": count_data}, "mn_sports_qq_nba_count"
        yield {"item": {"_id": uuid, "data": count_data, "home_team_name": home_team_name, "away_team_name": away_team_name, "start_time": start_time}, "collection": "mn_sports_qq_nba_count"}
