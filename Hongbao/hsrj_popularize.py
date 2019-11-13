# encoding=utf-8
from Hongbao.Source.Material import m_hsrj, m_hsrj2
from Room.Sub import get_all_win_by_name
from SendMsgByQQ.QQGUI import send_qq, send_msg_to_qun


qun_list = \
    list(set(get_all_win_by_name('找工作'))) + \
    list(set(get_all_win_by_name('军事'))) + \
    list(set(get_all_win_by_name('租房'))) + \
    list(set(get_all_win_by_name('拼车'))) + \
    list(set(get_all_win_by_name('兼职'))) + \
    list(set(get_all_win_by_name('赚钱')))


# 向qun中发消息
send_msg_to_qun(list(set(qun_list)), m_hsrj2, 60*60, source_dir='./Source/')