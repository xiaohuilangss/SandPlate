# encoding=utf-8
from Hongbao.Source.Material import m_hsrj
from Room.Sub import get_all_win_by_name
from SendMsgByQQ.QQGUI import send_qq, send_msg_to_qun


qun_list = \
    list(set(get_all_win_by_name('影子')))


# 向qun中发消息
send_msg_to_qun(qun_list, m_hsrj, 60*30, source_dir='./Source/', start_time='00:00:00', end_time='13:59:59')