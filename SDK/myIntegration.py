# encoding = utf-8
import pandas as pd
import numpy as np

from T_deri_test.Subfunction import lineInsert

"""
自定义积分函数，用于对离散点序列进行积分

原理：
    给定二维离散点数据，分x轴与y轴
    给定积分的起止x轴坐标

    对于曲线的每一部分，根据求梯形的计算方式，采用（“上底”+“下底”）*高/2的计算方法求得。
"""


def myIntegration(df_origin, x_axis_name, y_axis_name, x_start, x_end):
    """
    函数功能：给定一个二维点组成的序列，dataframe格式，以及起始位置，得出积分值

    :param df_origin:   原始数据
    :param x_axis_name: df中存储x轴的列的名字
    :param y_axis_name: df中存储y轴的列的名字
    :param x_start:     x起始值
    :param x_end:       y起始值
    :return:
    """

    # 判断起止时间是否在原始数据的定义域内
    if (x_start<np.min(df_origin[x_axis_name])) | (x_end > np.max(df_origin[x_axis_name])):
        print('函数 myIntegration：定义域超限！')
        return np.nan

    # 将起始x值构建成dataframe的索引
    index_df = pd.DataFrame(index=[x_start, x_end])

    # 将time设置成索引
    test_data = df_origin.set_index(keys=x_axis_name)

    # 将起始位置合并到原始数据中
    df_concat = pd.concat([index_df, test_data], axis=1)\
        .reset_index()\
        .rename(columns={'index': x_axis_name})\
        .sort_values(by=x_axis_name, ascending=True)

    # 对起始x值进行插值
    df_concat = lineInsert(df_concat, y_axis_name, x_axis_name)

    # 根据起始位置对数据进行截取
    df_concat = df_concat[df_concat[x_axis_name]>=x_start][df_concat[x_axis_name]<=x_end].sort_values(by=x_axis_name, ascending=True)

    # 求取前后时间间隔
    df_concat['next_'+x_axis_name] = df_concat[x_axis_name].shift(periods=-1)
    df_concat['time_span'] = df_concat.apply(lambda x: x['next_'+x_axis_name] - x[x_axis_name], axis=1)

    # 求取下一个时刻的值
    df_concat['next_'+y_axis_name] = df_concat[y_axis_name].shift(periods=-1)

    # 删除由于上下移动导致的空值
    df_concat = df_concat.dropna(how='any', axis=0)

    # 求取每一个单元的积分
    df_concat['sub_sum'] = df_concat.apply(lambda x: (x[y_axis_name]+x['next_'+y_axis_name])*x['time_span']/2, axis=1)

    # 求取最终的积分值
    integration_finale = np.sum(df_concat['sub_sum'])

    return integration_finale


# ----------------------------------- 测试 -------------------------------------
# test_data = pd.DataFrame(data=np.random.rand(100, 2), columns=['time', 'value']).sort_values(by='time',ascending=True)
#
#
# x_start = 0.4
# x_end = 0.8


# v_finale = myIntegration(df_origin=test_data, x_axis_name='time', y_axis_name='value', x_start=0.4, x_end=5)


# end=0