import win32gui

hwnd_title = dict()
hwnd_class = dict()


def get_all_hwnd_title(hwnd, arg):

	if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
		hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


def get_all_hwnd_class(hwnd, arg):

	if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
		hwnd_class.update({hwnd: win32gui.GetClassName(hwnd)})


def get_all_qq_win():

	win32gui.EnumWindows(get_all_hwnd_class, 0)
	h_c_list = [(h, c) for h, c in hwnd_class.items()]
	h_c_list_filter = list(filter(lambda x:  x[1] == 'TXGuiFoundation', h_c_list))

	return [win32gui.GetWindowText(x[0]) for x in h_c_list_filter]


def get_all_win_by_name(name):
	win32gui.EnumWindows(get_all_hwnd_title, 0)
	name_list = [t for h, t in hwnd_title.items()]
	name_list_filter = list(filter(lambda x: name in x, name_list))

	return name_list_filter


if __name__ == '__main__':

	r = get_all_qq_win()

	# r = win32gui.FindWindowEx(hwndParent=0, hwndChildAfter=0, lpszClass=None, lpszWindow='')
	r = win32gui.FindWindow('TXGuiFoundation', None)

	name_list = get_all_win_by_name('拼车')

	for h, t in hwnd_title.items():
		if t is not "":
			print(h, t)
