# coding = utf-8
import time
# from datetime import *
import datetime

import math

'''Function: get current system datetime
:return         datetime string format as:'2017-09-12 12:23:41'
'''


# 转换操作
def convert_datetime_to_str(datetime_param):
    return datetime.date.strftime(datetime_param, '%Y-%m-%d %H:%M:%S')


def convert_date_to_str(date_param):
    return datetime.date.strftime(date_param, '%Y-%m-%d')


def convert_str_to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')


def convert_str_to_date(date_str):
    if len(date_str) > 11:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
    else:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def date_str_std(date_str):

    date_str_sure = '%s' % date_str
    if not '-' in date_str_sure:
        return convert_date_to_str(datetime.datetime.strptime(date_str_sure, '%Y%m%d').date())
    else:
        return date_str_sure


def timeStd(date_str):
    """
    规整时间格式，原来的格式可能是12:32

    规整思路：

    根据“:”进行分割，判断分割后的单位数量，时分秒，没有的维度补充上


    :param date_str:
    :return:
    """


def dateStd(date_str):
    """
    函数功能：有些日期字符串格式为‘2018-8-21’的形式，就是说，在月或者日的数字中，只有个位数时，前面不会有0，
    这种格式与正常格式有出入，在按字符串进行筛选时会出错，所以需要对这种字符串进行“规整”
    :param date_str:
    :return:
    """
    if '/' in date_str:
        y, m, d = date_str.split('/')
    elif '-' in date_str:
        y, m, d = date_str.split('-')
    else:
        print('函数 dateStd：输入的日期格式不合格！原路返回！')
        return date_str

    if (int(m) < 10) & (len(m) == 1):
        m = '0' + m

    if (int(d) < 10) & (len(d) == 1):
        d = '0' + d

    return y+'-'+m+'-'+d


# 将时间转为秒数
def convert_time_str_to_second(input_str):

    result = input_str.strip().split(":")
    if len(result) == 3:
        h, m, s = result
        return int(h) * 3600 + int(m) * 60 + int(float(s))
    elif len(result) == 2:
        h, m = result

        return int(h) * 3600 + int(m) * 60


def convert_second_to_time_str(input_second):
    """
    将秒转为时间字符串（下面已经有函数实现了。。。。）
    :param input_second:
    :return:
    """
    second = input_second % 60
    minute = (input_second - second) % (60*60)
    hour = (input_second - second - minute*60)/(60*60)

    # int化、字符串化
    second = str(int(second))
    minute = str(int(minute))
    hour = str(int(hour))

    # 填0处理
    if len(hour) == 1:
        hour = '0' + hour
    if len(minute) == 1:
        minute = '0' + minute
    if len(second) == 1:
        second = '0' + second

    return hour + ':' + minute + ':' + second


def s2t(seconds):
    """
    将秒转为字符串形式的时间
    :param seconds:
    :return:
    """

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def DatetimeStr2Sec(s):

    '''
    convert a ISO format time to second
    from:2006-04-12 16:46:40 to:23123123
    把一个时间转化为秒
    '''
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return time.mktime(d.timetuple())


def DateStr2Sec(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d")
    return time.mktime(d.timetuple())


def Sec2Datetime(s):

    '''
    convert second to a ISO format time
    from: 23123123 to: 2006-04-12 16:46:40
    把给定的秒转化为定义的格式
    '''

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(s)))


# 获取操作
def get_current_datetime_str():
    datetime_now = datetime.datetime.now()
    return datetime.datetime.strftime(datetime_now, '%Y-%m-%d %H:%M:%S')


def get_current_date_str():
    datetime_now = datetime.datetime.now()
    return datetime.datetime.strftime(datetime_now, '%Y-%m-%d')


def get_current_date():
    return datetime.datetime.now().date()


def get_datestr_from_datetimestr(datetime_str):
    datetime_inner = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    return datetime.datetime.strftime(datetime_inner, '%Y-%m-%d')


def get_date_from_datetime_str(datetime_param):
    date_str = str(datetime_param)[0:10]
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def get_date_from_datetime(datetime_param):
    datetime_str = datetime.datetime.strftime(datetime_param, '%Y-%m-%d %H:%M:%S')
    date_str = datetime_str[0:10]
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


# 计算得到当前所在的季度，201703的格式
def get_quarter_date():
    date_split_str = get_current_date_str().split('-')
    year_str = date_split_str[0]
    month_str = date_split_str[1]

    year_int = int(year_str)
    month_int = int(month_str)

    # 判断当前季度
    quarter = math.floor((month_int-1)/3) +1
    return year_str + '0'+str(quarter)


# 加减操作
'''
字符串格式的时间日期的加减，以天为单位
将字符串转为日期格式后，进行天数的加减，然后在转回字符串

'''


def add_date_str(origin_date_str, days):
    origin_date = convert_str_to_date(origin_date_str)
    return convert_date_to_str(origin_date + datetime.timedelta(days=days))


def add_sec_to_datetime_str(origin_date_str, seconds):
    origin_date = convert_str_to_datetime(origin_date_str)
    return convert_datetime_to_str(origin_date + datetime.timedelta(seconds=seconds))


def minus_date_str(pos_date, net_date):
    return (convert_str_to_date(pos_date) - convert_str_to_date(net_date)).days


''' --------------------Some about conversion between timestamp with datetime------------------------------ '''
def get_date_from_timestamp(timestamp_para):
    date_str = get_datestr_from_datetimestr(str(timestamp_para))
    return convert_str_to_date(date_str)


# ---------------------------------------- 测试用 -----------------------------------------------

if __name__ == '__main__':

    r = add_sec_to_datetime_str('2019-02-04 12:33:15', -18)

    end = 0
