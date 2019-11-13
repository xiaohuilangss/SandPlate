# encoding=utf-8
""" =========================== 将当前路径及工程的跟目录添加到路径中 ============================ """
import sys
import os



curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("SandPlate\\")+len("SandPlate\\")]  # 获取myProject，也就是项目的根路径

sys.path.append('..')
sys.path.append(rootPath)

from Room.Sub import get_all_win_by_name
from SDK.MyTimeOPT import get_current_datetime_str
from SendMsgByQQ.QQGUI import send_qq
import time

note_str1 = \
"""
四方利群附近 宽敞朝南次卧出租！

房子介绍：
新房，两室一厅，80平，精装修，房子特干净清新，出租朝南次卧。
冰箱、热水器、空调、煤气灶、油烟机等一应俱全，
可做饭，拎包入住。

当前房间已经空出来了，看好后可以立马入住。
主卧住着一位人很好的小姐姐。
"""


note_str2 = \
"""
58同城有房子照片：
https://i.m.58.com/qd/hezu/39877045347346x.shtml?isself=1&707&utps=1381740504000

有意租住的小伙伴联系私聊实地看房！。

价格：
950/月，押一付三，价格可议
"""

note_str3 = \
"""
要求：
1、作息规律（很重要，晚上10点半后尽量保持安静）、
    有正当职业、品德优秀，好沟通、不吸烟！
2、不接受带宠物
3、女生或者情侣优先，人品好，有原则的男生也可以考虑。
"""

note_str4 = \
"""
联系方式：
小窗或者加本qq好友(工作时间不怎么看QQ，尽量加微信聊)
电话（微信）：13791930992


未来的室友，希望我们能够一起愉快的生活~
"""
qun_list = list(set(get_all_win_by_name('租房')))

while (get_current_datetime_str()[-8:] >= '06:00:00') & (get_current_datetime_str()[-8:] <= '12:00:00'):
    for qun in qun_list:
        try:
            send_qq(qun, note_str1)
            time.sleep(1.5)
            send_qq(qun, note_str2)
            time.sleep(1.5)
            send_qq(qun, note_str3)
            time.sleep(1.5)
            print(qun + '： 消息发送成功！\n------------------------\n\n')
        except Exception as e:
            print(qun + '： 消息发送失败！\n原因:\n' + str(e) + '\n------------------------\n\n')

    print('\n\n================== 大循环完成 ==================\n\n完成时间：' + get_current_datetime_str() + '\n')
    time.sleep(60*60*5)

    time.sleep(60*10)