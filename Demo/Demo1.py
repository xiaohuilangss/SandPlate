# coding=utf-8
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

rq_flag = False

while not rq_flag:
    try:
        headers = {'User-Agent': 'User-Agent:Mozilla/5.0'}
        resp = requests.get('http://live.win007.com/', headers=headers)        # 请求百度首页
        print(str(resp))
        if not '500' in str(resp):
            rq_flag = True
    except Exception as ex:
        print(str(ex))
        time.sleep(3)


print(resp)                                         # 打印请求结果的状态码
print(resp.content)                                 # 打印请求到的网页源码

bsobj = BeautifulSoup(resp.content, 'lxml')         # 将网页源码构造成BeautifulSoup对象，方便操作


ulist = []
trs = bsobj.find_all('tr')
for tr in trs:
    ui = []
    for td in tr:
        ui.append(td.string)
        ulist.append(ui)


end = 0



"""
#tr1_1744252 > td:nth-child(2) > a > font
"""