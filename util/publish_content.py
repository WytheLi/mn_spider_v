#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : li
# @Email   : wytheli168@163.com
# @Time    : 19-11-29 下午4:34
# @Description: 今日头条selenium发帖
# selenium文档网址： https://selenium-python-zh.readthedocs.io/en/latest/api.html#

import random
import time
import traceback
from contextlib import contextmanager

import cv2
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


from mn_spider_v.constants import CHROMEDRIVER_PATH
from util.proxy_test import auth


@contextmanager
def selenium(driver):
    try:
        yield
    except Exception as e:
        traceback.print_exc()
        time.sleep(1)


class ChromeDriver(object):
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.binary_location = '/opt/google/chrome/chrome'
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')  # 如果不加这个选项，有时定位会出现问题
        self.chrome_options.add_argument('--headless')  # 增加无界面选项
        self.chrome_options.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")
        # self.chrome_options.add_argument('Proxy-Authorization=%s' % auth)
        # self._driver = webdriver.Chrome(executable_path=config.CHROMEDRIVER_PATH, chrome_options=self._options)

        from pyvirtualdisplay import Display
        self.display = Display(visible=0, size=(800, 800))
        self.display.start()
        # 以下用单例模式创建对象
        self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)


class TouTiaoLogin(object):
    def __init__(self, username, password):
        self.url = "https://sso.toutiao.com/"
        self.username = username
        self.password = password
        self.cookies = []
        self.chromedriver = ChromeDriver()

    def login(self):
        """
        登录并获取cookies
        :param chromedriver:
        :return:
        """
        try:
            with selenium(self.chromedriver.driver):
                # driver = webdriver.Chrome('/home/joshu/PycharmProjects/toutiao_login/chromedriver')  # 选择Chrome浏览器
                # driver = webdriver.Firefox()
                self.chromedriver.driver.get(url=self.url)
                time.sleep(1)
                self.chromedriver.driver.find_element_by_id('login-type-account').click()
                time.sleep(1)
                # 输入用户名
                self.chromedriver.driver.find_element_by_id('user-name').click()
                self.chromedriver.driver.find_element_by_id('user-name').send_keys(self.username)
                # 输入密码
                self.chromedriver.driver.find_element_by_id('password').click()
                self.chromedriver.driver.find_element_by_id('password').send_keys(self.password)
                # 点击登录
                self.chromedriver.driver.find_element_by_id('bytedance-login-submit').click()
                time.sleep(1)

                # 获取背景图并保存
                background_url = self.chromedriver.wait.until(
                    # lambda x: x.find_element_by_xpath('//div[@id="verify-bar-box"]//img[1]')
                    lambda x: x.find_element_by_xpath(
                        '//div[@class="captcha-container"]//div[contains(@class, "captcha_verify_img--wrapper")]/img[1]')
                ).get_attribute('src')
                # 获取滑块图并保存
                slider_url = self.chromedriver.wait.until(
                    # lambda x: x.find_element_by_xpath('//div[@id="verify-bar-box"]//img[2]')
                    lambda x: x.find_element_by_xpath(
                        '//div[@class="captcha-container"]//div[contains(@class, "captcha_verify_img--wrapper")]/img[2]')
                ).get_attribute('src')

                with open('background.png', 'wb') as f:
                    resp = requests.get(background_url)
                    f.write(resp.content)
                with open('slider.png', 'wb') as f:
                    resp = requests.get(slider_url)
                    f.write(resp.content)
                time.sleep(2)

                distance = self._findfic(target='background.png', template='slider.png')
                # print(distance)
                # 初始滑块距离边缘 4 px
                trajectory = self._get_tracks(distance)
                # print(trajectory)

                # 等待按钮可以点击
                slider_element = self.chromedriver.wait.until(
                    # EC.element_to_be_clickable(
                    #     (By.CLASS_NAME, 'react-draggable sc-gqjmRU llQwoM'))
                    lambda x: x.find_element_by_xpath(
                        "//div[@class ='captcha_verify_slide--button slide-button___StyledDiv-sc-11qn0r0-0 dowsWu'] // div[@ class ='react-draggable sc-gqjmRU llQwoM'] / div")
                )

                # 添加行动链
                ActionChains(self.chromedriver.driver).click_and_hold(slider_element).perform()
                for track in trajectory['plus']:
                    ActionChains(self.chromedriver.driver).move_by_offset(
                        xoffset=track,
                        yoffset=round(random.uniform(1.0, 3.0), 1)
                    ).perform()
                time.sleep(0.5)

                for back_tracks in trajectory['reduce']:
                    ActionChains(self.chromedriver.driver).move_by_offset(
                        xoffset=back_tracks,
                        yoffset=round(random.uniform(1.0, 3.0), 1)
                    ).perform()
                #
                for i in [-4, 4]:
                    ActionChains(self.chromedriver.driver).move_by_offset(
                        xoffset=i,
                        yoffset=0
                    ).perform()

                time.sleep(0.1)
                ActionChains(self.chromedriver.driver).release().perform()
                time.sleep(2)
                # 域名过滤前的所有cookies
                self.cookies = self.chromedriver.driver.get_cookies()
                # print(self.cookies)
        except Exception as e:
            print(e)
            self._callback_fun()
            print("Callback to get cookies!")
        else:
            print("Get cookies successful!")

    def _findfic(self, target='background.png', template='slider.png'):
        """
        估算模块滑动所需距离
        :param target: 滑块背景图
        :param template: 滑块图片路径
        :return: 模板匹配距离
        """
        target_rgb = cv2.imread(target)
        target_gray = cv2.cvtColor(target_rgb, cv2.COLOR_BGR2GRAY)
        template_rgb = cv2.imread(template, 0)
        # 使用相关性系数匹配， 结果越接近1 表示越匹配
        # https://www.cnblogs.com/ssyfj/p/9271883.html
        res = cv2.matchTemplate(target_gray, template_rgb, cv2.TM_CCOEFF_NORMED)
        # opencv 的函数 minMaxLoc：在给定的矩阵中寻找最大和最小值，并给出它们的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # 因为滑块只需要 x 坐标的距离，放回坐标元组的 [0] 即可
        if abs(1 - min_val) <= abs(1 - max_val):
            distance = min_loc[0]
        else:
            distance = max_loc[0]
        return distance

    def _get_tracks(self, distance):
        """
        获取滑块偏移量列表
        :param distance: 缺口距离
        :return: 轨迹
        """
        # 分割加减速路径的阀值
        value = round(random.uniform(0.55, 0.75), 2)
        # 划过缺口 20 px
        distance += 20
        # 初始速度，初始计算周期， 累计滑动总距
        v, t, sum = 0, 0.3, 0
        # 轨迹记录
        plus = []
        # 将滑动记录分段，一段加速度，一段减速度
        mid = distance * value
        while sum < distance:
            if sum < mid:
                # 指定范围随机产生一个加速度
                # a = round(random.uniform(2.5, 3.5), 1)
                a = 10
            else:
                # 指定范围随机产生一个减速的加速度
                # a = -round(random.uniform(2.0, 3.0), 1)
                a = -10
            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            sum += s
            plus.append(round(s))

        # end_s = sum - distance
        # plus.append(round(-end_s))

        # 手动制造回滑的轨迹累积20px
        # reduce = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        reduce = [-6, -4, -6, -4]
        return {'plus': plus, 'reduce': reduce}

    def _callback_fun(self):
        """
        滑块验证错误回调
        :return:
        """
        try:
            self.login()
        except Exception as e:
            print(e)
            self._callback_fun()
            print("Callback to get cookies!")
        else:
            print("Get Cookies Successful!")


class TouTiaoPosted(object):
    def __init__(self, chromedriver, cookies):
        self.url = "https://www.toutiao.com/"
        self.chromedriver = chromedriver
        self.cookies = cookies

    def getPureDomainCookies(self):
        """
        获取指定domain的cookies
        :param cookies:
        :return:
        """
        temp = []
        for cookie in self.cookies:
            domain = cookie["domain"]
            if domain == "www.toutiao.com":
                temp.append(cookie)
        return temp

    def posted(self, content):
        """
        携带cookie去发帖
        :return:
        """
        # 过滤后拿到指定站点的cookies
        self.cookies = self.getPureDomainCookies()
        # print(self.cookies)
        for cookie in self.cookies:
            if "expiry" in cookie:
                del cookie["expiry"]
            self.chromedriver.driver.add_cookie(cookie)
        self.chromedriver.driver.get(self.url)
        self.chromedriver.driver.find_element_by_class_name('title-input').click()
        self.chromedriver.driver.find_element_by_class_name('title-input').send_keys(content)
        time.sleep(1)
        self.chromedriver.driver.find_element_by_class_name('upload-publish').click()
        time.sleep(1)
        print("Posted Successful！")


if __name__ == "__main__":
    # user = TouTiaoLogin("18229854080", "Lzw1911@")
    user = TouTiaoLogin("19901551995", "Fyy19920717")
    user = TouTiaoLogin("14928623347", "MN7777mn")
    user.login()

    t = TouTiaoPosted(user.chromedriver, user.cookies)
    t.posted("呼伦贝尔")
