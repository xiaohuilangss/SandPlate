# encoding=utf-8
""" =========================== 将当前路径及工程的跟目录添加到路径中 ============================ """
import sys
import os

from Room.Sub import get_all_win_by_name
from SDK.MyTimeOPT import get_current_datetime_str

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("SandPlate\\")+len("SandPlate\\")]  # 获取myProject，也就是项目的根路径

sys.path.append('..')
sys.path.append(rootPath)

from SDK.MyTimeOPT import get_current_datetime_str
from SendMsgByQQ.QQGUI import send_qq
import time

note_str1 = \
"""
不用盖楼，复制下面的码，打开淘宝或者天猫，直接领红包，一般是几块钱，运气好的更高！
"""


note_str2 = \
"""
【快来兑换你的双11红I包，可赢额外红I包】https://m.tb.cn/h.etQyNSR?sm=64355a 嚸↑↓擊鏈ㄣ接，再选择瀏覽●噐○咑閞ヽ；或復ず■淛整句话￥orm1YuW897g￥后咑閞手机天猫
"""

qun_list = \
    list(set(get_all_win_by_name('找工作'))) + \
    list(set(get_all_win_by_name('军事'))) + \
    list(set(get_all_win_by_name('租房')))


while (get_current_datetime_str()[-8:] >= '06:00:00') & (get_current_datetime_str()[-8:] <= '23:00:00'):
    for qun in qun_list:
        try:
            send_qq(qun, note_str1)
            time.sleep(0.5)
            send_qq(qun, note_str2)
            time.sleep(0.5)
            # send_qq(qun, note_str3)
            # time.sleep(1.5)
            print(qun + '： 消息发送成功！\n------------------------\n\n')
        except Exception as e:
            print(qun + '： 消息发送失败！\n原因:\n' + str(e) + '\n------------------------\n\n')

    print('\n\n================== 大循环完成 ==================\n\n完成时间：' + get_current_datetime_str() + '\n')
    time.sleep(60*30)