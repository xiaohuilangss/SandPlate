# encoding=utf-8

"""
推广文件夹中的东西
"""
import codecs
import glob
import os

from Hongbao.Sub import get_product_info

if __name__ == '__main__':

    # 获取产品列表
    r = get_product_info(r'C:/Users\paul\Desktop\文案')

    # 获取群列表
    qun_list = \
        list(set(get_all_win_by_name('影子')))

    send_all_product_to_all_qun(qun_list, r, 1.5, 0)

    end = 0

