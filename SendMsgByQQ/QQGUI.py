import win32gui
import win32con
import win32clipboard as w
import time


def getText():
	"""获取剪贴板文本"""
	w.OpenClipboard()
	d = w.GetClipboardData(win32con.CF_UNICODETEXT)
	w.CloseClipboard()
	return d


def setText(string):
	"""设置剪贴板文本"""
	w.OpenClipboard()
	w.EmptyClipboard()
	w.SetClipboardData(win32con.CF_UNICODETEXT, string)
	w.CloseClipboard()


def send_qq(towho, msge):
	"""发送qq消息
	to_who：qq消息接收人
	msg：需要发送的消息
	"""
	# 将消息写到剪贴板
	setText(msge)

	# 句柄list
	hand_list = []

	i = 0
	qq = win32gui.FindWindow(None, towho)
	if qq != 0:

		win32gui.SetWindowText(qq, towho + str(i))
		hand_list.append(qq)

		# 投递剪贴板消息到QQ窗体
		win32gui.SendMessage(qq, 258, 22, 2080193)
		win32gui.SendMessage(qq, 770, 0, 0)

		# 模拟按下回车键
		win32gui.SendMessage(qq, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
		win32gui.SendMessage(qq, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
	else:
		print('没有名字为 ' + towho + '的窗口！')
		return

	# 查找是否有同名窗口
	while qq != 0:
		i = i + 1
		qq = win32gui.FindWindow(None, towho)
		if qq != 0:
			win32gui.SetWindowText(qq, towho + str(i))
			hand_list.append(qq)

		# 投递剪贴板消息到QQ窗体
		win32gui.SendMessage(qq, 258, 22, 2080193)
		win32gui.SendMessage(qq, 770, 0, 0)

		# 模拟按下回车键
		win32gui.SendMessage(qq, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
		win32gui.SendMessage(qq, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

	# 恢复原先的名字
	if len(hand_list):
		r = [win32gui.SetWindowText(x, towho) for x in hand_list]


if __name__ == '__main__':
	send_qq('青岛租房群', '大家好')

""" -------------------------------- 测试 --------------------------------- """
# while(True):
#     send_qq(u'影子', '没事！')
#     time.sleep(3)