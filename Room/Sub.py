import win32gui

hwnd_title = dict()


def get_all_hwnd(hwnd, arg):

	if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
		hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


def get_all_win_by_name(name):
	win32gui.EnumWindows(get_all_hwnd, 0)
	name_list = [t for h, t in hwnd_title.items()]
	name_list_filter = list(filter(lambda x: name in x, name_list))

	return name_list_filter



if __name__ == '__main__':

	name_list = get_all_win_by_name('拼车')

	for h, t in hwnd_title.items():
		if t is not "":
			print(h, t)
