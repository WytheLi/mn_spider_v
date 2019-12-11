# !/usr/bin/python3
import sys
import time
import hashlib
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_version = sys.version_info

is_python3 = (_version[0] == 3)

orderno = "ZF20191298120NifqXV"
secret = "65a61c2fe56840488037cc507b6620f4"

ip = "forward.xdaili.cn"
port = "80"

ip_port = ip + ":" + port

timestamp = str(int(time.time()))
plan_text = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

if is_python3:
    plan_text = plan_text.encode()

md5_string = hashlib.md5(plan_text).hexdigest()
sign = md5_string.upper()
# print(sign)
auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

# print(auth)
proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
headers = {"Proxy-Authorization": auth,
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}


if __name__ == "__main__":
    # r = requests.get("http://2000019.ip138.com", headers=headers, proxies=proxy, verify=False, allow_redirects=False, )
    r = requests.get("https://www.baidu.com/?tn=06074089_21_pg", headers=headers, proxies=proxy, verify=False, allow_redirects=False, )
    r.encoding = 'utf8'
    print(r.status_code)
    # print(r.text)
    if r.status_code == 302 or r.status_code == 301:
        loc = r.headers['Location']
        print(loc)
        r = requests.get(loc, headers=headers, proxies=proxy, verify=False, allow_redirects=False)
        r.encoding = 'utf8'
        print(r.status_code)
        # print(r.text)
