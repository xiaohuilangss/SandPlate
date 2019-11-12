# encoding = utf-8

# 与时间相关的自定义函数文件


def stdMonthDate(month_str):

    """
    函数功能：将“2017.8”转成“2017.08”，否则在画图时会出现错乱，因为画图时8会大于12
    :param month_str:
    :return:
    """

    str_split = month_str.split('.')
    if int(str_split[1]) <10:
        str_split[1] = "0"+str_split[1]

    return str_split[0]+'.'+str_split[1]


def convertValue2Quarter(value):

    """
    函数功能：2018.5 --> '2018.2'
    :return:
    """
    decimal = value%1

    if decimal == 0:
        q_str = '1'
    elif decimal == 0.25:
        q_str = '2'
    elif decimal == 0.5:
        q_str = '3'
    elif decimal == 0.75:
        q_str = '4'

    year_str = str(math.floor(value))

    return year_str + '.' + q_str
