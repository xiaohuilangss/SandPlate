# coding:utf-8
import requests
import hashlib
import json
import time


class GETTaoBaoKeAPI(object):
	"""docstring for TaoBaoAPI"""

	def __init__(self, *args, **kwargs):
		# self.jindutiao()

		print("数据采集中，请稍后...")
		time.sleep(3)

	# 淘宝sign签名算法
	def get_Taobao_Sign(self, paramets):
		app_secret = "ad1aedab80473075e9e1bbdd540753fc"
		dict = sorted(paramets.iteritems(), key=lambda d: d[0])
		# 遍历出排序好的数据
		string = ""
		for i in range(len(dict)):
			for j in range(len(dict[i])):
				# 把排序好的数据遍历出并拼接在一起
				string = string + dict[i][j]
		pinjie = app_secret + string + app_secret
		# 为拼接好的字符串加密形成sign签名
		sign = ''
		# 把拼接的字符串通过MD5加密
		md = hashlib.md5()
		md.update(pinjie)
		sign = md.hexdigest()
		sign = sign.upper()
		# print "get_Taobao_sign=="+sign
		return sign

	def getTaoQiangGou(self):
		'''

		└ title                         String         连衣裙商品标题
		└ total_amount         Number         100总库存
		└ click_url                 String         http://s.click.taobao.com/t?e=x商品链接（是淘客商品返回淘客链接，非淘客商品返回普通h5链接）
		└ category_name         String         潮流女装类目名称
		└ zk_final_price         String         50.00淘抢购活动价
		└ end_time                 String  2016-08-09 13:00:00结束时间
		└ sold_num                 Number         50已抢购数量
		└ start_time                 String         2016-08-09 12:00:00开团时间
		└ reserve_price         String         100.00商品原价
		└ pic_url                         String         http: //img4.tbcdn.cn/tfscom/i4/189490253156622336/TB2bZuSsVXXXXcNXXXXXXXXXXXX_!!0-juitemmedia.jpg商品主图
		└ num_iid                         Number         123商品ID
		total_results                Number        20        返回的结果数

		'''
		play2 = {'app_key': '23287826', 'method': 'taobao.tbk.ju.tqg.get',
				 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'adzone_id': '37564171',
				 'start_time': '2019-08-25 00:00:00', 'end_time': '2019-12-31 00:00:00', 'format': 'json', 'v': '2.0',
				 'sign_method': 'md5',
				 'fields': 'click_url,pic_url,reserve_price,zk_final_price,total_amount,sold_num,title,category_name,start_time,end_time'}

		play2["sign"] = self.get_Taobao_Sign(play2)

		cont_dict = requests.post('http://gw.api.taobao.com/router/rest', params=play2)
		json_qianggou_con = json.loads(cont_dict.text)

		zhuan = json_qianggou_con['tbk_ju_tqg_get_response']['results']['results']

		print(zhuan)
		return zhuan