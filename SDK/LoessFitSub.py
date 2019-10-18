# encoding=utf-8

"""
本脚本保存Loess拟合的相关子函数
"""
from numpy import *
import numpy as np
import pandas as pd

def loess(x, h, xp, yp):
    """
    函数功能：使用loess算法拟合x处的值
    :param x:   x位置值
    :param h:   权重函数宽度  单位即x轴的单位
    :param xp:  待拟合的x轴点
    :param yp:  待拟合的y轴点
    :return:
    """
    w = exp(-0.5 * ((x - xp) / h) ** 2) / sqrt(2 * pi * h ** 2)
    b = sum(w * xp) * sum(w * yp) - sum(w) * sum(w * xp * yp)
    b /= sum(w * xp) ** 2 - sum(w) * sum(w * xp ** 2)
    a = (sum(w * yp) - b * sum(w * xp)) / sum(w)
    return a + b * x


def loessFit(df_potArray, x_axis_name, y_axis_name, bandWidth):
    """
    函数功能：给定要拟合的数据点，和加权函数的宽度，拟合出loess曲线

    给定原始数据的df，以及“x轴和y轴的列名”

    :param df_potArray:     df格式，第一列为x轴，第二列为y轴
    :param bandWidth:
    :param x_axis_name:     df中x轴的名字
    :return:
    """
    pot_array = df_potArray.loc[:, [x_axis_name, y_axis_name]].values
    fit_result = df_potArray.apply(lambda x: loess(x[x_axis_name], bandWidth, pot_array[:, 0], pot_array[:, 1]), axis=1)
    return fit_result

if __name__ == '__main__':

    df = pd.DataFrame({'x': np.random.rand(100), 'y': np.random.rand(100)})

    df['fit'] = loessFit(df, 'x', 'y', 0.2)

    end=0
