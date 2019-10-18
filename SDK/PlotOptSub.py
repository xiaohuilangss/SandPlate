# encoding = utf-8
import math


def addXticklabel(ax, df_date_S, x_amount, fontsize=5, rotation=90):

    """
    将字符串列用作x轴标签
    :param ax:
    :param df_date_S:   sh_index['date']
    :param x_amount:    x轴最多40个label，多了太密
    :return:
    """
    xticks = range(0, len(df_date_S), int(math.ceil(len(df_date_S) / x_amount)))
    xticklabels_all_list = list(df_date_S.sort_values(ascending=True))
    xticklabels_all = [xticklabels_all_list[n] for n in xticks]

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels_all, rotation=rotation, fontsize=fontsize)

    return ax


