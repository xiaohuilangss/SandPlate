# encoding=utf-8

"""
推广文件夹中的东西
"""
import codecs
import glob
import os

import time

from Hongbao.Sub import get_product_info, send_all_product_to_all_qun
from Room.Sub import get_all_win_by_name

if __name__ == '__main__':


    # 获取产品列表
    r = get_product_info(r'C:/Users\paul\Desktop\文案')

    # 获取群列表
    qun_list = \
        list(set(get_all_win_by_name('找工作'))) + \
        list(set(get_all_win_by_name('军事'))) + \
        list(set(get_all_win_by_name('租房'))) + \
        list(set(get_all_win_by_name('拼车'))) + \
        list(set(get_all_win_by_name('兼职'))) + \
        list(set(get_all_win_by_name('吃鸡'))) + \
        list(set(get_all_win_by_name('赚钱')))

    while True:

        send_all_product_to_all_qun(qun_list, r, 1.5, 2)
        time.sleep(60*60*4)

