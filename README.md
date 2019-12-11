#### 项目环境
```txt
数据库环境： mongodb, mysql, redis
浏览器以及对应的selenim浏览器驱动： google-chrome, chromedriver
linux服务器上的虚拟窗口： apt-get install xvfb
```

#### 启动爬虫
```sh
pip3 install -r requirements.txt

vim /home/wytheli/.virtualenvs/mn_spider/lib/python3.5/site-packages/scrapy/core/downloader/handlers/http11.py
# 注释掉以下两行
if isinstance(agent, self._TunnelingAgent):
    headers.removeHeader(b'Proxy-Authorization')

cd [项目目录]

# 启动celery worker
celery -D -A celery_tasks worker -l info -f logs/celery.log

# 启动爬虫
nohup python3 -u run.py > logs/log.log 2>&1 &
```

#### 脚本启动
```sh
#!/bin/sh
while [ 1 ]; do
  nohup /root/.virtualenvs/mn_spider/bin/python3 -u /root/mn_spider_scrapy/run.py > logs/log.log 2>&1 &
done
```