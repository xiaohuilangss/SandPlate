# encoding=utf-8

"""
推广文件夹中的东西
"""
import codecs
import glob
import os

import time

from Room.Sub import get_all_win_by_name
from SendMsgByQQ.QQGUI import send_qq, send_qq_pic


def get_product_info(root_url):

    """
    获取产品信息表
    :param root_url:
    :return:
    """

    # 存储结果
    product_list = []

    # 遍历其下的文件夹（商品）
    fs = os.listdir(root_url)

    for product_path_rela in fs:

        # 去除模板
        if product_path_rela == '模板':
            continue

        product_path_abs = os.path.join(root_url, product_path_rela)

        # 获取购买关键字
        try:
            with open(product_path_abs + '/文本.txt', 'r') as f:
                buy_key = f.read()
                buy_key =buy_key.replace('復製评论', '復製这一段话')

        except Exception as e:
            with open(product_path_abs + '/文本.txt', 'r', encoding='utf-8') as f:
                buy_key = f.read()
                buy_key =buy_key.replace('復製评论', '復製这一段话')

        # 获取介绍
        with open(product_path_abs + '/介绍.txt', 'r', encoding="gb18030") as f:
            introduce_text = f.read()

        # 获取图片路径
        img_list = glob.glob(product_path_abs + '/*.bmp')
        if not len(img_list):
            img_list = \
                glob.glob(product_path_abs + '/*.jpg') + \
                glob.glob(product_path_abs + '/*.png') + \
                glob.glob(product_path_abs + '/*.jpeg')

        product_list.append({
            'product_name': product_path_abs,
            'product_introduce': introduce_text,
            'product_image_list': img_list,
            'product_buy_key': buy_key
        })

    return product_list


def send_single_product_to_single_qun(product_dict, qun, sleep_time):
    """
    向一个群发送一个产品
    :param product_dict:
    :param qun:
    :return:
    """

    # 发送介绍
    if len(product_dict['product_introduce']) > 0:
        send_qq(qun, product_dict['product_introduce'])
        time.sleep(sleep_time - 1)

    # 发送图片
    if len(product_dict['product_image_list']) > 0:
        for image in product_dict['product_image_list']:

            send_qq_pic(qun, image)
            time.sleep(sleep_time)

    # 发送buy key
    send_qq(qun, product_dict['product_buy_key'])
    time.sleep(sleep_time - 1)


def send_all_product_to_all_qun(qun_list, product_list, inter_sleep_time, product_sleep_time):
    """
    将所有product 发送到所有群
    :param qun_list:
    :param product_list:
    :param sleep_time:
    :return:
    """

    for product in product_list:

        for qun in qun_list:
            send_single_product_to_single_qun(product, qun, inter_sleep_time)

        time.sleep(product_sleep_time)


if __name__ == '__main__':

    # 获取产品列表
    r = get_product_info(r'C:/Users\paul\Desktop\文案')

    # 获取群列表
    qun_list = \
        list(set(get_all_win_by_name('影子')))

    send_all_product_to_all_qun(qun_list, r, 1.5, 0)



    end = 0

