# encoding=utf-8
from Room.Sub import get_all_win_by_name
from SDK.MyTimeOPT import get_current_datetime_str
from SendMsgByQQ.QQGUI import send_qq
import time


qun_list = \
    list(set(get_all_win_by_name('找工作'))) + \
    list(set(get_all_win_by_name('军事'))) + \
    list(set(get_all_win_by_name('租房')))
