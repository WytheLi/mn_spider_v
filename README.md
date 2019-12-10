#### 项目环境
```txt
数据库环境： mongodb, mysql, redis
浏览器以及对应的selenim浏览器驱动： google-chrome, chromedriver
linux服务器上的虚拟窗口： apt-get install xvfb
```

#### 启动爬虫
```sh
nohup python3 -u run.py > logs/log.log 2>&1 &
```
