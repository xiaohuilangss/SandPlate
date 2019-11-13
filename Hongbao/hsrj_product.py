# encoding=utf-8

"""
推广文件夹中的东西
"""
import codecs
import glob
import os


if __name__ == '__main__':

    dir = r'C:/Users\paul\Desktop\文案'

    # 遍历其下的文件夹（商品）
    fs = os.listdir(dir)

    for product_path_rela in fs:
        product_path_abs = os.path.join(dir, product_path_rela)

        # 获取购买关键字
        with open(product_path_abs + '/文本.txt', 'r', encoding='utf-8') as f:
            key_buy = f.read()

        # 获取介绍
        with open(product_path_abs + '/介绍.txt', 'r', encoding='utf-8') as f:
            introduce_buy = f.read()

        # 获取图片路径
        img_list = glob.glob(product_path_abs + '/*.bmp')
        if not len(img_list):
            img_list = \
                glob.glob(product_path_abs + '/*.jpg') + \
                glob.glob(product_path_abs + '/*.png') + \
                glob.glob(product_path_abs + '/*.jpeg')


        end = 0

