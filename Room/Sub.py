import win32gui

import win32con

from SendMsgByQQ.QQGUI import send_qq, send_qq_hwnd

hwnd_title = dict()
hwnd_class = dict()


def get_all_hwnd_title(hwnd, arg):

	if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
		hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


def get_all_hwnd_class(hwnd, arg):

	if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
		hwnd_class.update({hwnd: win32gui.GetClassName(hwnd)})


def get_all_qq_win():
	"""
	获取桌面上所有的qq窗口
	:return:
	"""

	win32gui.EnumWindows(get_all_hwnd_class, 0)
	h_c_list = [(h, c) for h, c in hwnd_class.items()]
	h_c_list_filter = list(filter(lambda x:  x[1] == 'TXGuiFoundation', h_c_list))

	return [(x[0], win32gui.GetWindowText(x[0])) for x in h_c_list_filter]


def get_all_win_by_name(name):
	win32gui.EnumWindows(get_all_hwnd_title, 0)
	name_list = [t for h, t in hwnd_title.items()]
	name_list_filter = list(filter(lambda x: name in x, name_list))

	return name_list_filter


if __name__ == '__main__':

	r = get_all_qq_win()

	for people in r:

		win32gui.SetWindowPos(people[0], win32con.HWND_TOPMOST, 600, 300, 600, 600, win32con.SWP_SHOWWINDOW)
		send_qq_hwnd(people[0], '你好')
		print(people[1] + '：发送消息成功！')

	# r = win32gui.FindWindowEx(hwndParent=0, hwndChildAfter=0, lpszClass=None, lpszWindow='')
	r = win32gui.FindWindow('TXGuiFoundation', None)

	name_list = get_all_win_by_name('拼车')

	for h, t in hwnd_title.items():
		if t is not "":
			print(h, t)
