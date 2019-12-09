# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re

from scrapy import signals

from logging import getLogger

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from mn_spider_v import constants


class MnSpiderVSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MnSpiderVDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# 该下载中间件开启后，所有爬虫都得selenium渲染
class SeleniumDownloaderMiddleware(object):
    # 在Middleware里面的process_request()方法里对每个抓取请求进行处理，
    # 启动浏览器并进行页面渲染，
    # 再将渲染后的结果构造一个HtmlResponse对象返回
    # selenium文档网址： https://selenium-python-zh.readthedocs.io/en/latest/api.html#
    def __init__(self, timeout=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.add_argument('--no-sandbox')
        # self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')  # 如果不加这个选项，有时定位会出现问题
        self.chrome_options.add_argument('--headless')  # 增加无界面选项
        self.chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        from pyvirtualdisplay import Display
        self.display = Display(visible=0, size=(800, 800))
        self.display.start()
        self.browser = webdriver.Chrome(executable_path=constants.CHROMEDRIVER_PATH, chrome_options=self.chrome_options)
        # self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        """

        :param request: Request对象
        :param spider: Spider对象
        :return: HtmlResponse
        """
        # 判断域名，特定的域名才通过该中间件
        # print(request.url.split("/")[2])
        if request.url.split("/")[2] in ["sports.qq.com",]:
            self.logger.debug('Webdriver is Starting')
            print("Webdriver is Starting")
            print(request.url)
            # page = request.meta.get('page', 1)
            try:
                self.browser.get(request.url)
                # 显式等待
                # 如果出现期望页面， 构造渲染成功的HtmlResponse 200页面对象返回给爬虫解析；
                # 否则构造HtmlResponse 500页面对象返回给爬虫
                # if page > 1:
                #     input = self.wait.until(
                #         EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))
                #     submit = self.wait.until(
                #         EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))
                #     input.clear()
                #     input.send_keys(page)
                #     submit.click()
                # self.wait.until(
                #     EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
                # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'host-goals')))
                # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'data-info')))
                # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'content-col')))
                return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                    status=200)
            except TimeoutException:
                return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'))
