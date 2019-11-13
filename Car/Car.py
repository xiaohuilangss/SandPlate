# encoding=utf-8
""" =========================== 将当前路径及工程的跟目录添加到路径中 ============================ """
import sys
import os



curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("SandPlate\\")+len("SandPlate\\")]  # 获取myProject，也就是项目的根路径

sys.path.append('..')
sys.path.append(rootPath)

from SendMsgByQQ.QQGUI import send_qq
import time
from Room.Sub import get_all_win_by_name
from SDK.MyTimeOPT import get_current_datetime_str

note_str1 = \
"""
人找车，今天下午（具体时间可以商量），平度同和(在平度南高速口附近)到青岛市北台东，一个人，顺路的老乡小窗联系！
"""
qun_list = list(set(get_all_win_by_name('拼车'))) + list(set(get_all_win_by_name('顺风车')))

while (get_current_datetime_str()[-8:] >= '06:00:00') & (get_current_datetime_str()[-8:] <= '23:00:00'):
    for qun in qun_list:
        try:
            send_qq(qun, note_str1)
            time.sleep(1.5)
            print(qun + '： 消息发送成功！\n------------------------\n\n')
        except Exception as e:
            print(qun + '： 消息发送失败！\n原因:\n' + str(e) + '\n------------------------\n\n')

    print('\n\n================== 大循环完成 ==================\n\n完成时间：' + get_current_datetime_str() + '\n')
    time.sleep(60*30)