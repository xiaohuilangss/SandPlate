# encoding=utf-8
from Hongbao.Source.Material import m_hsrj
from Room.Sub import get_all_win_by_name
from SDK.MyTimeOPT import get_current_datetime_str
from SendMsgByQQ.QQGUI import send_qq, send_msg_to_qun
import time


qun_list = \
    list(set(get_all_win_by_name('五行缺钱')))


# 向qun中发消息
send_msg_to_qun(qun_list, m_hsrj, 60*30, source_dir='./Source/')