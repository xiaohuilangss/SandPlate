# encoding = utf-8

"""
reportlab相关的子函数
"""
import random
import math
import pandas as pd
import numpy as np
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

from reportlab.lib.pagesizes import letter

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet

# 画图相关
from reportlab.graphics.shapes import Drawing, PolyLine, colors, Auto
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker


from reportlab.pdfbase.pdfmetrics import stringWidth

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from JZ_Volt_Destribute.Global.Global_Info import electricityPriceData, electricityPriceHour
from JZ_Volt_Destribute.Global.VoltClass import *
from JZ_Volt_Destribute.ShowGraph.FormatSubfunction import ExtractJsonToColumn
from SDK.AboutTimeSub import convertValue2Quarter
from SDK.MyTimeOPT import Sec2Datetime

pdfmetrics.registerFont(TTFont('song', 'SURSONG.TTF'))
pdfmetrics.registerFont(TTFont('hei', 'SIMHEI.TTF'))

from reportlab.lib import fonts
fonts.addMapping('song', 0, 0, 'song')
fonts.addMapping('song', 0, 1, 'song')
fonts.addMapping('song', 1, 0, 'hei')
fonts.addMapping('song', 1, 1, 'hei')


"""
# 本脚本是一些与reportlab包有关的子函数
# 同时也设置reportlab中常用的一些import，其他文件可以通过import该文件来方便地引入常用依赖
"""
def addFront(canvas_param, theme, subtitle, pagesize=letter):
    """
    函数功能：为pdf文档添加功能，分“主题”、“副标题”两部分
    :param canvas:
    :param pagesize: 页面大小，默认A4
    :param theme: 主题字符串
    :param subtitle: 副标题字符串
    :return:
    """
    PAGE_WIDTH = pagesize[0]
    PAGE_HEIGHT = pagesize[1]

    # 设置主标题字体并打印主标题
    canvas_param.setFont("song", 30)
    canvas_param.drawString((PAGE_WIDTH-stringWidth(theme, fontName='song', fontSize=30))/2.0, PAGE_HEIGHT*0.618, theme)

    # 设置副标题字体并打印副标题
    canvas_param.setFont("song", 10)
    canvas_param.drawString((PAGE_WIDTH-stringWidth(theme, fontName='song', fontSize=30))/2.0, PAGE_HEIGHT*0.15, subtitle)

    canvas_param.showPage()

    return canvas_param


def add_legend(draw_obj, chart, pos_x, pos_y):

    """
    函数功能：voltGroupDisplayByBar函数的子函数
    :param draw_obj:
    :param chart:
    :return:
    """
    legend = Legend()
    # legend.variColumn = True
    legend.autoXPadding = True

    legend.alignment = 'right'
    legend.fontName = 'song'
    legend.x = pos_x
    legend.y = pos_y
    legend.colorNamePairs = Auto(obj=chart)
    draw_obj.add(legend)


def genBcDrawing(data, data_name, width, height):

    note_list = data_name

    drawing = Drawing(width=width, height=height)
    bc = VerticalBarChart()
    # bc.x = 50
    # bc.y = 50
    # bc.height = 125
    bc.width = width
    bc.data = data
    bc.valueAxis.valueMin = 0
    bc.barSpacing = 10

    # bc.valueAxis.valueMax = 50
    # bc.valueAxis.valueStep = 10
    bc.categoryAxis.style = 'stacked'
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30

    barFillColors = [
        colors.red, colors.green, colors.white, colors.blue, colors.yellow,
        colors.pink, colors.purple, colors.lightgreen, colors.darkblue, colors.lightyellow,
        colors.fidred, colors.greenyellow, colors.gray, colors.blueviolet, colors.lightgoldenrodyellow]

    for i in range(len(data)):
        bc.bars[i].name = note_list[i]

        # 最多只支持15种颜色，多出的设置为红色
        if i < 15:
            bc.bars[i].fillColor = barFillColors[i]
        else:
            bc.bars[i].fillColor = colors.red

    bc.categoryAxis.categoryNames = [str(i) for i in range(1, 25, 1)]
    drawing.add(bc)

    # 增加legend
    add_legend(drawing, bc, pos_x=10, pos_y=-10)

    return drawing


def voltGroupDisplayByBar(canvas_param, df, note_list, pos_x, pos_y, width, height):

    """
    函数功能：使用bar图对一组电表进行展示，着重展示其相关关系，以胶州园区用电调度为背景

    :param canvas_param:    画布
    :param df:              多个电表某一属性组成的数据矩阵，例如“用电量”属性
    :return:
    """

    if 'sum' in df.columns:
        df = df.drop('sum', axis=1)

    data = list(map(lambda x: tuple(float(m) for m in x), df.values.T))

    drawing = genBcDrawing(data, note_list, width, height)

    renderPDF.draw(drawing=drawing, canvas=canvas_param, x=pos_x, y=pos_y)

    return canvas_param


def moveVoltToOthers(volt_list, maxAmount, minPercent, colName):

    """
    函数功能：在对多只表进行展示的时候，如果表的数量过多，会造成展示效果不佳，比如颜色种类多导致颜色的辨识度不足等。
                需要将影响较小的表归类到Others中，以减少表的数量，突出重要表的功能。

                前提：today数据中应该经过record_type筛选

    :param volt_list: 表的列表
    :param maxAmount: 最大表数量，函数据此将次要表归类到others中
    :param minPercent: 占比percent，如果表的影响程度低于该值，则将该表置于others中
    :param colName: 列的名字
    :return: 整理后的表的list，以及others中包含的表的名字，一个note_list
    """

    # 计算各个电表当天的数值总合
    r1 = []
    for v in volt_list:
        r1.append((np.sum([float(e) for e in v.today[colName]]), v))

    # 计算总电量
    today_total_e = np.sum([e[0] for e in r1])

    # 计算各表所占percent
    r2 = [(e[0] / today_total_e, e[0], e[1]) for e in r1]

    # 按所占percent进行排序
    r2.sort(key=lambda x: x[0], reverse=True)

    # 筛选出属于others的电表
    others = []

    for v in r2:

        if (r2.index(v) > maxAmount - 2) | (v[0] < minPercent):
            others.append(v)

    remain = list(filter(lambda x: x not in others, r2))
    # 结果：others remain

    # others 只包含一只表的情况下，此函数没有意义，所以直接返回原来的电表列表即可
    if len(volt_list) - len(remain) <= 2:
        return volt_list

    if len(others) > 0:
        df_list_other = list(map(lambda x: x[2], others))

        (values, percent, note_info) = concatVolt(df_list_other, colName)

        values = values.rename(columns={'sum': colName}).reset_index()
        values['device_name'] = '其他'
        values['channel'] = 'others'

        # 构造虚拟电表“others”
        volt_others = VoltMeter(building='', pos='', note='其他', deviceKey='others')
        volt_others.add_today_data(values)

        # 将虚拟电表others添加到主list中
        voltListFinale = list(map(lambda x: x[2], remain))
        voltListFinale.append(volt_others)
    else:
        voltListFinale = volt_list

    return voltListFinale


def genMultVoltDf(volt_list, col_name, maxAmount=8, minPercent=0.01):

    # 从多表中整理数据，前提为：volt的today字段中已经添加了原始的数据
    # （重要！today中添加的应该是该设备当天的原始数据，即完全从数据库）
    volt_list_pro = []

    # 删除没有df中没有数据的表
    volt_list_filter = list(filter(lambda x: not x.today.empty, volt_list))

    if len(volt_list_filter) == 0:
        print('函数 genMultVoltDf：所列电表皆没有数据！')
        return ()

    # 从电表列表的原始数据中整理提取每天数据
    for v in volt_list_filter:

        # 如果该dk的数据包含多个表地址，则根据表地址二次筛选
        if 'channel' in v.today.columns:
            if len(v.today.groupby(by='channel')) > 1:
                df_today_f = v.today[v.df_today.channel == v.meter_address]
            else:
                df_today_f = v.today
        else:
            df_today_f = v.today

        # 将‘data’列中的数据提取
        df_today_f = ExtractJsonToColumn(df_today_f, 'data')

        # 删除数据中record_code 为2的行
        if 'record_type' in df_today_f.columns:
            df_today_f = df_today_f[~df_today_f.record_type.isin(['2'])]

        v.add_today_data(df_today_f)

        # 将当天数据添加到电表对象中
        volt_list_pro.append(v)

    # 对电表进行数量约束，不重要的电表归总在虚拟电表“其他”中
    volt_list_pro = moveVoltToOthers(volt_list_pro, maxAmount=maxAmount, minPercent=minPercent, colName=col_name)

    # 数据合并
    (values, percent, note_list) = concatVolt(voltDfList=volt_list_pro, col_name=col_name)

    return values, percent, note_list


def addMultVoltPageToPdf(canvas_param,
                         volt_list,
                         col_name,
                         maxAmount=8,
                         minPercent=0.01,
                         pos_x=10,
                         pos_y=letter[1]*0.5,
                         width=letter[0]*0.8,
                         height=letter[1]*0.4):

    """
    函数功能：
                增加多表对比显示页，用于对多只表组合的系统的一个全面展示

    :param canvas_param:        画布
    :param volt_list:           表的list
    :param col_name:
    :return:
    """

    # 数据合并
    result = genMultVoltDf(volt_list, col_name)

    if len(result) == 0:
        canvas_param.drawString(x=10, y=letter[1] - 100, text='本页所列电表皆没有数据！')
        canvas_param.showPage()
        return canvas_param
    else:
        (values, percent, note_list) = result

    # 画柱状图并添加到画布中
    voltGroupDisplayByBar(canvas_param=canvas_param,
                          df=values,
                          note_list=note_list,
                          pos_x=pos_x,
                          pos_y=pos_y,
                          width=width,
                          height=height)

    # 结束当前页,不宜在函数中结束当前页的编辑，因为其他函数也可能会编辑本页！
    # canvas_param.showPage()
    return canvas_param


def genPotArrayByDkList(df_today, dk_list):
    """
    函数功能：根据给定的dk list 生成pot array，用于画图
    :return:
    """

    building_df = df_today
    pot_list = []

    for dk in dk_list:
        df_dk_specified = building_df[building_df.device_key == dk]

        if df_dk_specified.empty:
            print('函数 genPotArrayByDkList：没有设备 ' + dk + ' 的数据！')
            continue

        df_Ext_1 = ExtractJsonToColumn(df_dk_specified, 'data')
        df_Ext_2 = ExtractJsonToColumn(df_Ext_1, 'function')

        if 'current_temp' in df_Ext_2.columns:
            df_Ext_3 = df_Ext_2.loc[:, ['current_temp', 'data_time']].dropna(how='any', axis=0)

            # 生成pot点图
            pot = ExtractPointFromDf_DateX(df_origin=df_Ext_3, date_col='data_time', y_col='current_temp')

        elif 'temperature' in df_Ext_2.columns:
            df_Ext_3 = df_Ext_2.loc[:, ['temperature', 'data_time']].dropna(how='any', axis=0)

            # 生成pot点图
            pot = ExtractPointFromDf_DateX(df_origin=df_Ext_3, date_col='data_time', y_col='temperature')
        elif df_Ext_2.empty:
            print('函数 genPotArrayByDkList：没有该设备的温度数据！')
            return []

        pot_list.append(pot)

    # 转变成tuple格式
    return list(map(lambda x: tuple(x), pot_list))


def addZHZFSummary(canvas_para, build, opc_df, history_today):

    c = canvas_para
    b = build

    # ------------------------------------------ 整理电量数据 ---------------------------------------

    result = genMultVoltDf(b['subDevList'], 'electricity')

    if len(result) == 0:
        c.drawString(x=10, y=letter[1] - 100, text='本页所列电表皆没有数据！')
        c.showPage()
        return c
    else:
        (values, percent, note_list) = result

    # 计算总电量
    elec_sum = values['sum'].sum()

    # ------------------------------------------ 整理电费数据 ---------------------------------------

    # 获取value值
    df_zhzf = values

    # 将str转为float
    df_zhzf = df_zhzf.applymap(lambda x: float(x))

    # 添加小时价格
    df_zhzf['hour_price'] = electricityPriceHour

    # 计算价格
    df_price = df_zhzf.apply(lambda x: x[~df_zhzf.columns.isin(['sum', 'hour_price'])] * x['hour_price'], axis=1)
    df_price_sum = df_price.apply(lambda x: np.sum(x.values), axis=1)
    price_sum = df_price_sum.sum()

    # ------------------------- 综合站房第一页：显示用电量图、电费阶梯图及用电价格图 ------------------------------

    # 显示“总用电量”和“总电费”
    str_pos_y = 90
    c.drawString(x=10, y=letter[1] - str_pos_y, text='本日综合站房 总耗    电量：  ' + '%2.1f' %elec_sum + '  kWh')
    c.drawString(x=10, y=letter[1] - str_pos_y-20, text='本日综合站房 共耗电费约：  ' + '%2.1f' %price_sum + '  元')

    c.setLineWidth(0.5)
    c.line(10, letter[1] - str_pos_y - 40, letter[0]*0.7, letter[1] - str_pos_y - 40)

    # 画电量图
    voltGroupDisplayByBar(canvas_param=c,
                          df=values,
                          note_list=note_list,
                          pos_x=10,
                          pos_y=letter[1] * 0.65,
                          width=letter[0] * 0.8,
                          height=letter[1] * 0.2)

    # 添加阶梯电价图
    c = addElectricPrice(canvas_param=c, pos_x=10, pos_y=letter[1] * 0.4, width=letter[0] * 0.8,
                         height=letter[1] * 0.1)

    # 画价格图
    drawing_price = genBcDrawing(df_price.values.T, list(map(lambda x: x + '电费', note_list)), width=letter[0] * 0.8,
                                 height=letter[1] * 0.2)
    renderPDF.draw(drawing=drawing_price, canvas=c, x=10, y=letter[1] * 0.25)

    # 为电费图添加备注
    c.line(10, letter[1] * 0.12, letter[0] * 0.8, letter[1] * 0.12)

    c.setFont("song", 7)
    c.drawString(10, letter[1] * 0.10, '备注：')
    c.drawString(10, letter[1] * 0.08, '           1、该电费图是依据每小时耗电量及胶州园区的阶梯电价（一般工商业电价35~110千伏）计算而来。单位为元！')
    c.drawString(10, letter[1] * 0.06, '           2、阶梯电价存在半点时刻的分界点，此时用平均法处理。')
    c.drawString(10, letter[1] * 0.04, '                例如：3点半~4点半电价为1元，4点半~5点半电价为1.5元，则认为4点~5点的电价为1.25元。')

    c.showPage()

    # 画电量图
    voltGroupDisplayByBar(canvas_param=c,
                          df=values,
                          note_list=note_list,
                          pos_x=10,
                          pos_y=letter[1] * 0.8,
                          width=letter[0] * 0.8,
                          height=letter[1] * 0.2)

    if not opc_df.empty:

        # 增加温度曲线图
        c = addAcTemp_webservice(canvas_param=c, desigocc_df_today=opc_df, pos_x=10, pos_y=letter[1] * 0.45, width=letter[0] * 0.8,
                      height=letter[1] * 0.2)

        # 增加功率曲线图
        c = addAcPower_webservice(canvas_param=c, desigocc_df_today=opc_df, pos_x=10, pos_y=letter[1] * 0.1, width=letter[0] * 0.8,
                       height=letter[1] * 0.2)

        c.showPage()

        # 增加1号厂房室内温度
        c = addF1TempPage_webservice(canvas_param=c, desigocc_df_today=opc_df)

        # 增加5号厂房室内温度
        c = addF5TempPage_webservice(canvas_param=c, desigocc_df_today=opc_df)

        # 增加试制中心室内温度
        # c = addSZZXTempPage_webservice(canvas_param=c, desigocc_df_today=opc_df)

    else:
        c.showPage()
        print('函数 addZHZFSummary：从opc数据库下载的数据为空！')

    # 增加存储于楼宇平台中的温度传感器
    if not history_today.empty:

        # ------------------------ 增加1楼温度展示 ---------------------------
        pot_qt = genPotArrayByDkList(df_today=history_today, dk_list=['00005BHG', '000086KP', '0000GH4K', '00004G69'])
        draw_qt = genLPDrawing(data=pot_qt,
                               data_note=['前台休息室-东', '前台休息室-西', '前台大厅-东', '前台大厅-西'],
                               timeAxis='time',
                               height=letter[1]*0.15)
        renderPDF.draw(drawing=draw_qt, canvas=c, x=10, y=letter[1] * 0.7)

        pot_zt = genPotArrayByDkList(df_today=history_today,
                                     dk_list=['00004830', '0000GR3Q', '0000EODK', '0000DTM7', '000057W8', '0000GX9U'])
        if len(pot_zt) > 0:
            draw_zt = genLPDrawing(data=pot_zt,
                                   data_note=['西展厅-中区', '西展厅-东区', '西展厅-西区', '东展厅-东区', '东展厅-中区', '东展厅-西区'],
                                   timeAxis='time',
                                   height=letter[1]*0.15)

            renderPDF.draw(drawing=draw_zt, canvas=c, x=10, y=letter[1] * 0.4)
        else:
            print('函数 addZHZFSummary：没有 试制中心 展厅的温度数据！')
        c.showPage()

        # ------------------ 增加试制中心2楼室内温度 -------------------------
        pot_f2_1 = genPotArrayByDkList(df_today=history_today,
                                       dk_list=['0000JP6Y', '000088YK', '00007MV6', '0000JWUO', '000011ZJ'])

        draw_f2_1 = genLPDrawing(data=pot_f2_1,
                                 data_note=['试制中心-201', '试制中心-202', '试制中心-203', '试制中心-205', '试制中心-206'],
                                 timeAxis='time',
                                 height=letter[1]*0.15)

        renderPDF.draw(drawing=draw_f2_1, canvas=c, x=10, y=letter[1] * 0.7)

        pot_f2_2 = genPotArrayByDkList(df_today=history_today, dk_list=['0000L99D', '0000FFL2', '00006TGQ', '00007HH3'])
        draw_f2_2 = genLPDrawing(data=pot_f2_2,
                                 data_note=['试制中心-209', '试制中心-210', '试制中心-211', '试制中心-212'],
                                 timeAxis='time',
                                 height=letter[1]*0.15)

        renderPDF.draw(drawing=draw_f2_2, canvas=c, x=10, y=letter[1] * 0.4)
        c.showPage()

        # ----------------------- 增加试制中心3楼的室内温度 ---------------------------
        pot_f3_1 = genPotArrayByDkList(df_today=history_today,
                                       dk_list=['0000CQUX', '0000L5OQ', '00006MS0', '00004KCA', '0000866N', '0000LE1C'])

        draw_f3_1 = genLPDrawing(data=pot_f3_1,
                                 data_note=['试制中心-301', '试制中心-302西', '试制中心-302东', '试制中心-303西', '试制中心-303东', '试制中心-305'],
                                 timeAxis='time',
                                 height=letter[1]*0.15)

        renderPDF.draw(drawing=draw_f3_1, canvas=c, x=10, y=letter[1] * 0.7)

        pot_f3_2 = genPotArrayByDkList(df_today=history_today, dk_list=['00005DV2', '0000LHTL', '00001DY6', '0000K7AB', '0000GLGL', '000086NR'])
        draw_f3_2 = genLPDrawing(data=pot_f3_2,
                                 data_note=['试制中心-306东', '试制中心-306中', '试制中心-306西', '试制中心-307', '试制中心-308东', '试制中心-308西'],
                                 timeAxis='time',
                                 height=letter[1]*0.15)

        renderPDF.draw(drawing=draw_f3_2, canvas=c, x=10, y=letter[1] * 0.4)

        pot_f3_2 = genPotArrayByDkList(df_today=history_today, dk_list=['000018ZX', '0000BYM6', '0000H42H', '0000L8Y5'])
        draw_f3_2 = genLPDrawing(data=pot_f3_2,
                                 data_note=['试制中心-309', '试制中心-310', '试制中心-东休息区', '试制中心-西休息区'],
                                 timeAxis='time',
                                 height=letter[1]*0.15)

        renderPDF.draw(drawing=draw_f3_2, canvas=c, x=10, y=letter[1] * 0.1)

        c.showPage()

    return c


def getPercent(x):
    """
    函数功能：函数concatVolt的子函数
    :param x:
    :return:
    """

    sumValue = x['sum']
    if sumValue == 0:
        sumValue = 1   # 防止除数为零

    return list(map(lambda y: float(y)/sumValue, x))


def concatVolt(voltDfList, col_name):

    """
    函数功能：将多个电表的dataframe按照时间进行合并，可以指定相应的列
                同时返回该电表的描述list，便于画图之用

                前提：电表对象中已经填充了当天的数据！

    :param voltDfList: 电表dataframe 列表
    :param col_name      指定的列
    :return:
    """

    # 将电表当天的数据拿出，作为一列
    voltDfList_final = list(map(lambda x: x.today, voltDfList))

    # 过滤掉空的df
    voltDfList_final = list(filter(lambda x:not x.empty,voltDfList_final))

    if len(voltDfList_final) == 0:
        print('函数 concatVolt：将要被合并的DataFrame都是空的，返回空Df结束函数！')
        return pd.DataFrame()

    # 将df列表中的某一列抽取
    voltDfList_SpecialCol = list(map(lambda x: x.loc[:, ['update_time', col_name]].rename(
        columns={col_name: col_name + x.head(1)['channel'].values[0]}), voltDfList_final))

    # 将各个df的索引改为列update_time
    voltDfList_SetIndex = list(map(lambda x: x.set_index(keys='update_time'), voltDfList_SpecialCol))

    # 将多个df按时间合并
    df_concat = pd.concat(voltDfList_SetIndex, axis=1)

    # 求解每一行的和
    df_concat['sum'] = df_concat.apply(lambda x: np.sum(list(map(lambda y: float(y), x.values))), axis=1)

    # 求解每一电量的百分比
    df_percent = df_concat.apply(lambda x: getPercent(x), axis=1)

    # 拿出设备描述List，用于画图之用，首先删除空的df
    df_list = list(filter(lambda x: len(x.today) != 0, voltDfList))
    note_list = list(map(lambda x: x.today.head(1)['device_name'].values[0], df_list))

    return df_concat, df_percent, note_list


def filterVoltDataByRecordType(voltList, record_type):
    """
    函数功能：根据record_type 筛选数据,入参record_type为要保留的数据
    :param voltList:
    :return:
    """
    result = []
    for v in voltList:
        if len(v.today) > 0:
            v.today = v.today[v.today.record_type.isin([record_type])]

        result.append(v)

    return result


def genVirtualVoltDf(voltList, colName, device_name):
    """
    函数功能：有时存在区域没有总表的情况，需要求多个表的电量和，此时将用到此函数，注意，colName往往为“electricity”
    :param voltList:
    :param colName:
    :return:
    """

    # 过滤空的df
    voltList = list(filter(lambda x: not x.today.empty, voltList))

    if len(voltList) == 0:
        print('函数 genVirtualVoltDf：所给原始电表皆无数据！')
        return pd.DataFrame()

    # 根据record_type 过滤数据
    voltList = filterVoltDataByRecordType(voltList, '1')

    # 将各电表电量求和
    (values, percent, note_list) = concatVolt(voltList, colName)

    values['device_name'] = device_name
    values['channel'] = 'virtual'+str(random.randint(1, 100000))

    # 生成虚拟表的数据,注意，将index reset，以便于普通数据相统一
    return values.rename(columns={'sum': colName}).reset_index()


def addAcTemp(canvas_param, opc_df_today,pos_x, pos_y, width, height):

    total_df = opc_df_today

    #  取出
    # “室外天气”、
    # “冷却侧供水温度”、
    # “冷却侧回水温度”、
    # “冷冻侧供水温度”、
    # “冷冻侧回水温度”
    total_df_OAT = total_df[total_df.browse_name == 'OA-T']

    total_df_CSSWT = total_df[total_df.browse_name == 'CS-SWT']
    total_df_CSRWT = total_df[total_df.browse_name == 'CS-RWT']

    total_df_FSSWT = total_df[total_df.browse_name == 'FS-SWT']
    total_df_FSRWT = total_df[total_df.browse_name == 'FS-RWT']

    # 生成5个变量相应的点阵
    data_OAT = ExtractPointFromDf_DateX(df_origin=total_df_OAT, date_col='present_value_source_timestamp',
                                        y_col='present_value_value')

    data_CSSWT = ExtractPointFromDf_DateX(df_origin=total_df_CSSWT, date_col='present_value_source_timestamp',
                                          y_col='present_value_value')
    data_CSRWT = ExtractPointFromDf_DateX(df_origin=total_df_CSRWT, date_col='present_value_source_timestamp',
                                          y_col='present_value_value')

    data_FSSWT = ExtractPointFromDf_DateX(df_origin=total_df_FSSWT, date_col='present_value_source_timestamp',
                                          y_col='present_value_value')
    data_FSRWT = ExtractPointFromDf_DateX(df_origin=total_df_FSRWT, date_col='present_value_source_timestamp',
                                          y_col='present_value_value')

    data_origin = [tuple(data_OAT), tuple(data_CSSWT), tuple(data_CSRWT), tuple(data_FSSWT), tuple(data_FSRWT)]

    # 定义各曲线标签
    data_name_origin = ['室外温度', '冷却侧供水温度', '冷却侧回水温度', '冷冻侧供水温度', '冷冻侧回水温度']

    # 处理某条线没有数据的情况，若不处理“没有数据”的情况，画线的时候会报错！
    data = []
    data_name = []

    for i in range(0, len(data_origin)):
        if len(data_origin[i]) != 0:
            data.append(data_origin[i])
            data_name.append(data_name_origin[i])

    if len(data) == 0:
        print('函数 addAcTemp：原始df解析后没有想要的温度数据！')
        return canvas_param

    c = canvas_param
    # c.setFont("song", 10)

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()
    # lp.x = 50
    # lp.y = 50
    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义各曲线颜色
    lp.lines[0].strokeColor = colors.blue
    lp.lines[1].strokeColor = colors.red
    lp.lines[2].strokeColor = colors.lightgreen
    lp.lines[3].strokeColor = colors.orange
    lp.lines[4].strokeColor = colors.darkgreen

    for i in range(0, len(data)):
        lp.lines[i].name = data_name[i]
        lp.lines[i].symbol = makeMarker('FilledCircle', size=0.5)
        lp.lines[i].strokeWidth = 0.2

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 60*60*24
    lp.xValueAxis.valueSteps = [n for n in range(0, 60*60*24, 60*60)]
    lp.xValueAxis.labelTextFormat = lambda x: str(s2t(x))[0:2]
    lp.yValueAxis.valueMin = 0
    # lp.yValueAxis.valueMax = 50
    # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-10)

    renderPDF.draw(drawing=drawing, canvas=c, x=pos_x, y=pos_y)

    return c


def addAcPower(canvas_param, opc_df_today,pos_x, pos_y, width, height):

    total_df = opc_df_today

    #  取出
    # “离心机1号实时功率”、
    # “离心机2号实时功率”、
    # “螺杆机实时功率”

    total_df_01P = total_df[total_df.browse_name == 'Chilling_unit1_D1_CH-01-Load']
    total_df_02P = total_df[total_df.browse_name == 'Chilling_unit2_D2_CH-02-Load']
    total_df_03P = total_df[total_df.browse_name == 'Chilling_unit3_D3_CH-03-Load']

    # 生成5个变量相应的点阵
    data_01P = ExtractPointFromDf_DateX(df_origin=total_df_01P, date_col='present_value_source_timestamp',
                                        y_col='present_value_value')

    data_02P = ExtractPointFromDf_DateX(df_origin=total_df_02P, date_col='present_value_source_timestamp',
                                          y_col='present_value_value')

    data_03P = ExtractPointFromDf_DateX(df_origin=total_df_03P, date_col='present_value_source_timestamp',
                                          y_col='present_value_value')

    data_origin = [tuple(data_01P), tuple(data_02P), tuple(data_03P)]

    # 定义各曲线标签
    data_name_origin = ['离心机1号实时功率', '离心机2号实时功率', '螺杆机实时功率']

    # 处理某条线没有数据的情况，若不处理“没有数据”的情况，画线的时候会报错！
    data = []
    data_name = []

    for i in range(0, len(data_origin)):
        if len(data_origin[i]) != 0:
            data.append(data_origin[i])
            data_name.append(data_name_origin[i])

    if len(data) == 0:
        print('函数 addAcTemp：原始df解析后没有想要的冷机功率数据！')
        return canvas_param

    c = canvas_param
    # c.setFont("song", 10)

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()
    # lp.x = 50
    # lp.y = 50
    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义各曲线颜色
    lp.lines[0].strokeColor = colors.blue
    lp.lines[1].strokeColor = colors.red
    lp.lines[2].strokeColor = colors.lightgreen
    lp.lines[3].strokeColor = colors.orange
    lp.lines[4].strokeColor = colors.darkgreen

    for i in range(0, len(data)):
        lp.lines[i].name = data_name[i]
        lp.lines[i].symbol = makeMarker('FilledCircle', size=0.5)
        lp.lines[i].strokeWidth = 0.05

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 60*60*24
    lp.xValueAxis.valueSteps = [n for n in range(0, 60*60*24, 60*60)]
    lp.xValueAxis.labelTextFormat = lambda x: str(s2t(x))[0:2]
    lp.yValueAxis.valueMin = 0
    # lp.yValueAxis.valueMax = 50
    # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-10)

    # 将画布添加到pdf中
    renderPDF.draw(drawing=drawing, canvas=c, x=pos_x, y=pos_y)

    return c


def addElectricPrice(canvas_param, pos_x, pos_y, width, height):

    # 电价数据
    data = electricityPriceData

    # 定义各曲线标签
    # data_name = ['一般工商业电价（1-10千伏）', '大工业电价（1-10千伏）', '一般工商业电价（35-110千伏）', '大工业电价（35-110千伏）']
    data_name = ['一般工商业电价（35-110千伏）']

    c = canvas_param
    # c.setFont("song", 10)

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()
    # lp.x = 50
    # lp.y = 50
    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义各曲线颜色
    lp.lines[0].strokeColor = colors.blue
    lp.lines[1].strokeColor = colors.red
    lp.lines[2].strokeColor = colors.darkgreen
    lp.lines[3].strokeColor = colors.black

    for i in range(0, len(data)):
        lp.lines[i].name = data_name[i]
        # lp.lines[i].symbol = makeMarker('FilledCircle', size=0.5)
        lp.lines[i].strokeWidth = 1

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 24
    lp.xValueAxis.valueSteps = [n for n in range(0, 24, 1)]
    lp.xValueAxis.labelTextFormat = lambda x: str(x)
    lp.yValueAxis.valueMin = 0
    # lp.yValueAxis.valueMax = 50
    # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-10)

    # 将画布添加到pdf中
    renderPDF.draw(drawing=drawing, canvas=c, x=pos_x, y=pos_y)

    return c


def genLPDrawing(data, data_note, width=letter[0]*0.8, height=letter[1]*0.25, timeAxis='day', y_min_zero=False):
    """
    函数功能：生成Drawing之用
    :return:
    """

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()
    # lp.x = 50
    # lp.y = 50
    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义颜色集
    barFillColors = [
        colors.red, colors.green, colors.blue, colors.darkgoldenrod,
        colors.pink, colors.purple, colors.lightgreen, colors.darkblue, colors.lightyellow,
        colors.fidred, colors.greenyellow, colors.gray, colors.white,colors.blueviolet, colors.lightgoldenrodyellow]

    for i in range(0, len(data)):
        lp.lines[i].name = data_note[i]
        lp.lines[i].symbol = makeMarker('FilledCircle', size=0.5)
        lp.lines[i].strokeWidth = 0.2
        lp.lines[i].strokeColor = barFillColors[i]

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    x_min = data[0][0][0]
    x_max = data[0][-1][0]

    lp.xValueAxis.valueMin = x_min
    lp.xValueAxis.valueMax = x_max

    if timeAxis=='day':
        step = int(((x_max - x_min) / (60 * 60 * 24)) / 30) + 1

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), 60 * 60 * 24 * step)]
        lp.xValueAxis.labelTextFormat = lambda x: str(Sec2Datetime(x)[0:10])
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18
        if y_min_zero:
            lp.yValueAxis.valueMin = 0

        # lp.yValueAxis.valueMax = 50
        # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
    if timeAxis=='time':

        lp.xValueAxis.valueMin = 0
        lp.xValueAxis.valueMax = 60 * 60 * 24
        lp.xValueAxis.valueSteps = [n for n in range(0, 60 * 60 * 24, 60 * 60)]
        lp.xValueAxis.labelTextFormat = lambda x: str(s2t(x))[0:2]

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    elif timeAxis=='quarter':

        step = int(((x_max - x_min)/0.25) / 30) + 1

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), int(math.ceil(0.25 * step)))]
        lp.xValueAxis.labelTextFormat = lambda x: convertValue2Quarter(x)
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    elif timeAxis=='year':

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), 1)]
        lp.xValueAxis.labelTextFormat = lambda x: str(x)
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    elif timeAxis=='month':

        lp.xValueAxis.valueSteps = list(map(lambda x:x[0],data[0]))
        lp.xValueAxis.labelTextFormat = lambda x: str(Sec2Datetime(x))[0:7]
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-20)

    return drawing


def addAcTemp_webservice(canvas_param, desigocc_df_today, pos_x, pos_y, width, height):

    total_df = desigocc_df_today

    #  取出
    # “室外天气”、
    # “冷却侧供水温度”、
    # “冷却侧回水温度”、
    # “冷冻侧供水温度”、
    # “冷冻侧回水温度”
    total_df_OAT = total_df[total_df.object_id == 'System1:GmsDevice_1_7030_1']

    total_df_CSSWT = total_df[total_df.object_id == 'System1:GmsDevice_1_7001_1']
    total_df_CSRWT = total_df[total_df.object_id == 'System1:GmsDevice_1_7001_2']

    total_df_FSSWT = total_df[total_df.object_id == 'System1:GmsDevice_1_7001_3']
    total_df_FSRWT = total_df[total_df.object_id == 'System1:GmsDevice_1_7001_4']

    # 生成5个变量相应的点阵
    data_OAT = ExtractPointFromDf_DateX(df_origin=total_df_OAT, date_col='value_time',
                                        y_col='node_value')

    data_CSSWT = ExtractPointFromDf_DateX(df_origin=total_df_CSSWT, date_col='value_time',
                                          y_col='node_value')

    data_CSRWT = ExtractPointFromDf_DateX(df_origin=total_df_CSRWT, date_col='value_time',
                                          y_col='node_value')

    data_FSSWT = ExtractPointFromDf_DateX(df_origin=total_df_FSSWT, date_col='value_time',
                                          y_col='node_value')

    data_FSRWT = ExtractPointFromDf_DateX(df_origin=total_df_FSRWT, date_col='value_time',
                                          y_col='node_value')

    data_origin = [tuple(data_OAT), tuple(data_CSSWT), tuple(data_CSRWT), tuple(data_FSSWT), tuple(data_FSRWT)]

    # 定义各曲线标签
    data_name_origin = ['室外温度', '冷却侧供水温度', '冷却侧回水温度', '冷冻侧供水温度', '冷冻侧回水温度']

    # 处理某条线没有数据的情况，若不处理“没有数据”的情况，画线的时候会报错！
    data = []
    data_name = []

    for i in range(0, len(data_origin)):
        if len(data_origin[i]) != 0:
            data.append(data_origin[i])
            data_name.append(data_name_origin[i])

    if len(data) == 0:
        print('函数 addAcTemp：原始df解析后没有想要的温度数据！')
        return canvas_param

    c = canvas_param
    # c.setFont("song", 10)

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()
    # lp.x = 50
    # lp.y = 50
    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义各曲线颜色
    lp.lines[0].strokeColor = colors.blue
    lp.lines[1].strokeColor = colors.red
    lp.lines[2].strokeColor = colors.lightgreen
    lp.lines[3].strokeColor = colors.orange
    lp.lines[4].strokeColor = colors.darkgreen

    for i in range(0, len(data)):
        lp.lines[i].name = data_name[i]
        lp.lines[i].symbol = makeMarker('FilledCircle', size=0.5)
        lp.lines[i].strokeWidth = 0.2

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 60*60*24
    lp.xValueAxis.valueSteps = [n for n in range(0, 60*60*24, 60*60)]
    lp.xValueAxis.labelTextFormat = lambda x: str(s2t(x))[0:2]
    lp.yValueAxis.valueMin = 0
    # lp.yValueAxis.valueMax = 50
    # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-10)

    renderPDF.draw(drawing=drawing, canvas=c, x=pos_x, y=pos_y)

    return c


def addAcPower_webservice(canvas_param, desigocc_df_today, pos_x, pos_y, width, height):

    total_df = desigocc_df_today

    #  取出
    # “离心机1号实时功率”、
    # “离心机2号实时功率”、
    # “螺杆机实时功率”

    total_df_01P = total_df[total_df.object_id == 'System1:GmsDevice_1_2_24']
    total_df_02P = total_df[total_df.object_id == 'System1:GmsDevice_1_2_25']
    total_df_03P = total_df[total_df.object_id == 'System1:GmsDevice_1_2_59']

    # 生成5个变量相应的点阵
    data_01P = ExtractPointFromDf_DateX(df_origin=total_df_01P, date_col='value_time',
                                        y_col='node_value')

    data_02P = ExtractPointFromDf_DateX(df_origin=total_df_02P, date_col='value_time',
                                        y_col='node_value')

    data_03P = ExtractPointFromDf_DateX(df_origin=total_df_03P, date_col='value_time',
                                        y_col='node_value')

    data_origin = [tuple(data_01P), tuple(data_02P), tuple(data_03P)]

    # 定义各曲线标签
    data_name_origin = ['离心机1号实时功率', '离心机2号实时功率', '螺杆机实时功率']

    # 处理某条线没有数据的情况，若不处理“没有数据”的情况，画线的时候会报错！
    data = []
    data_name = []

    for i in range(0, len(data_origin)):
        if len(data_origin[i]) != 0:
            data.append(data_origin[i])
            data_name.append(data_name_origin[i])

    if len(data) == 0:
        print('函数 addAcTemp：原始df解析后没有想要的冷机功率数据！')
        return canvas_param

    c = canvas_param
    # c.setFont("song", 10)

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()
    # lp.x = 50
    # lp.y = 50
    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义各曲线颜色
    lp.lines[0].strokeColor = colors.blue
    lp.lines[1].strokeColor = colors.red
    lp.lines[2].strokeColor = colors.lightgreen
    lp.lines[3].strokeColor = colors.orange
    lp.lines[4].strokeColor = colors.darkgreen

    for i in range(0, len(data)):
        lp.lines[i].name = data_name[i]
        lp.lines[i].symbol = makeMarker('FilledCircle', size=0.5)
        lp.lines[i].strokeWidth = 0.05

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 60*60*24
    lp.xValueAxis.valueSteps = [n for n in range(0, 60*60*24, 60*60)]
    lp.xValueAxis.labelTextFormat = lambda x: str(s2t(x))[0:2]
    lp.yValueAxis.valueMin = 0
    # lp.yValueAxis.valueMax = 50
    # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-10)

    # 将画布添加到pdf中
    renderPDF.draw(drawing=drawing, canvas=c, x=pos_x, y=pos_y)

    return c


def addF1TempPage_webservice(canvas_param, desigocc_df_today):
    """
    函数功能：增加1号厂房的室内温度显示
    :param canvas_param:
    :param desigocc_df_today:
    :param pos_x:
    :param pos_y:
    :param width:
    :param height:
    :return:
    """
    total_df = desigocc_df_today

    #  取出
    # “离心机1号实时功率”、
    # “离心机2号实时功率”、
    # “螺杆机实时功率”
    f1_6 = total_df[total_df.object_id == 'System1:GmsDevice_1_7022_3']
    f1_7 = total_df[total_df.object_id == 'System1:GmsDevice_1_7022_7']
    f1_8 = total_df[total_df.object_id == 'System1:GmsDevice_1_7022_10']
    f2_8 = total_df[total_df.object_id == 'System1:GmsDevice_1_7006_4']

    # 生成5个变量相应的点阵
    f1_6_pot = ExtractPointFromDf_DateX(df_origin=f1_6, date_col='value_time',
                                        y_col='node_value')

    f1_7_pot = ExtractPointFromDf_DateX(df_origin=f1_7, date_col='value_time',
                                        y_col='node_value')

    f1_8_pot = ExtractPointFromDf_DateX(df_origin=f1_8, date_col='value_time',
                                        y_col='node_value')

    f2_8_pot = ExtractPointFromDf_DateX(df_origin=f2_8, date_col='value_time',
                                        y_col='node_value')

    data_origin = [tuple(f1_6_pot), tuple(f1_7_pot), tuple(f1_8_pot), tuple(f2_8_pot)]

    # 定义各曲线标签
    data_name_origin = ['1号厂房-6', '1号厂房-7', '1号厂房-8', '2号厂房-8']

    # 处理某条线没有数据的情况，若不处理“没有数据”的情况，画线的时候会报错！
    data = []
    data_name = []

    for i in range(0, len(data_origin)):
        if len(data_origin[i]) != 0:
            data.append(data_origin[i])
            data_name.append(data_name_origin[i])

    if len(data) == 0:
        print('函数 addAcTemp：原始df解析后没有想要的温度数据！')
        return canvas_param

    c = canvas_param

    drawing_f1 = genLPDrawing(data=data_origin, data_note=data_name_origin, timeAxis='time')

    # 将画布添加到pdf中
    renderPDF.draw(drawing=drawing_f1, canvas=c, x=10, y=letter[1]*0.5)

    c.showPage()

    return c


def addF5TempPage_webservice(canvas_param, desigocc_df_today):

    """
    函数功能：增加5号厂房的室内温度显示
    :param canvas_param:
    :param desigocc_df_today:
    :param pos_x:
    :param pos_y:
    :param width:
    :param height:
    :return:
    """

    c = canvas_param

    total_df = desigocc_df_today

    #  取出
    # “离心机1号实时功率”、
    # “离心机2号实时功率”、
    # “螺杆机实时功率”

    f5_1f6 = total_df[total_df.object_id == 'System1:GmsDevice_1_7011_4']
    f5_1f7 = total_df[total_df.object_id == 'System1:GmsDevice_1_7011_6']
    f5_1f8 = total_df[total_df.object_id == 'System1:GmsDevice_1_7011_10']

    f5_2f1 = total_df[total_df.object_id == 'System1:GmsDevice_1_7012_4']
    f5_2f2 = total_df[total_df.object_id == 'System1:GmsDevice_1_7012_6']
    f5_2f3 = total_df[total_df.object_id == 'System1:GmsDevice_1_7012_11']

    f5_2f6 = total_df[total_df.object_id == 'System1:GmsDevice_1_7014_4']
    f5_2f7 = total_df[total_df.object_id == 'System1:GmsDevice_1_7014_6']
    f5_2f8 = total_df[total_df.object_id == 'System1:GmsDevice_1_7014_11']

    f5_3f2 = total_df[total_df.object_id == 'System1:GmsDevice_1_7016_1']

    # 生成5个变量相应的点阵
    f5_1f6_pot = ExtractPointFromDf_DateX(df_origin=f5_1f6, date_col='value_time', y_col='node_value')
    f5_1f7_pot = ExtractPointFromDf_DateX(df_origin=f5_1f7, date_col='value_time', y_col='node_value')
    f5_1f8_pot = ExtractPointFromDf_DateX(df_origin=f5_1f8, date_col='value_time', y_col='node_value')

    f5_2f1_pot = ExtractPointFromDf_DateX(df_origin=f5_2f1, date_col='value_time', y_col='node_value')
    f5_2f2_pot = ExtractPointFromDf_DateX(df_origin=f5_2f2, date_col='value_time', y_col='node_value')
    f5_2f3_pot = ExtractPointFromDf_DateX(df_origin=f5_2f3, date_col='value_time', y_col='node_value')

    f5_2f6_pot = ExtractPointFromDf_DateX(df_origin=f5_2f6, date_col='value_time', y_col='node_value')
    f5_2f7_pot = ExtractPointFromDf_DateX(df_origin=f5_2f7, date_col='value_time', y_col='node_value')
    f5_2f8_pot = ExtractPointFromDf_DateX(df_origin=f5_2f8, date_col='value_time', y_col='node_value')

    f5_3f2_pot = ExtractPointFromDf_DateX(df_origin=f5_3f2, date_col='value_time', y_col='node_value')

    # 处理某个传感器没有数据的情况
    data_1f_origin = []
    data_name_1f = []
    for dev_data in [(tuple(f5_1f6_pot), '5号厂房-lf6'),
                     (tuple(f5_1f7_pot), '5号厂房-1f7'),
                     (tuple(f5_1f8_pot), '5号厂房-1f8')]:

        if len(dev_data[0])>0:
            data_1f_origin.append(dev_data[0])
            data_name_1f.append(dev_data[1])
        else:
            print('函数 addF5TempPage_webservice：设备 ' + dev_data[1] + ' 没有数据！')

    data_2f_origin = []
    data_name_2f = []
    for dev_data in [(tuple(f5_2f1_pot), '5号厂房-2f1'),
                     (tuple(f5_2f2_pot), '5号厂房-2f2'),
                     (tuple(f5_2f3_pot), '5号厂房-2f3'),
                     (tuple(f5_2f6_pot), '5号厂房-2f6'),
                     (tuple(f5_2f7_pot), '5号厂房-2f7'),
                     (tuple(f5_2f8_pot), '5号厂房-2f8')]:

        if len(dev_data[0])>0:
            data_2f_origin.append(dev_data[0])
            data_name_2f.append(dev_data[1])
        else:
            print('函数 addF5TempPage_webservice：设备 ' + dev_data[1] + ' 没有数据！')

    if len(f5_3f2_pot) > 0:
        data_3f_origin = [tuple(f5_3f2_pot)]
        data_name_3f = ['5号厂房-3f2']
    else:
        data_3f_origin = []
        data_name_3f = []

    # 处理某条线没有数据的情况，若不处理“没有数据”的情况，画线的时候会报错！
    drawing_f1 = genLPDrawing(data=data_1f_origin, data_note=data_name_1f, timeAxis='time', height=letter[1]*0.15)
    drawing_f2 = genLPDrawing(data=data_2f_origin, data_note=data_name_2f, timeAxis='time', height=letter[1]*0.15)
    drawing_f3 = genLPDrawing(data=data_3f_origin, data_note=data_name_3f, timeAxis='time', height=letter[1]*0.15)

    # 将画布添加到pdf中
    renderPDF.draw(drawing=drawing_f1, canvas=c, x=10, y=letter[1]*0.7)
    renderPDF.draw(drawing=drawing_f2, canvas=c, x=10, y=letter[1]*0.4)
    renderPDF.draw(drawing=drawing_f3, canvas=c, x=10, y=letter[1]*0.1)

    c.showPage()

    return c


def addSZZXTempPage_webservice(canvas_param, desigocc_df_today):

    """
    函数功能：增加试制中心的室内温度显示
    :param canvas_param:
    :param desigocc_df_today:
    :param pos_x:
    :param pos_y:
    :param width:
    :param height:
    :return:
    """

    c = canvas_param

    total_df = desigocc_df_today

    SZZX_101 = total_df[total_df.object_id == 'System1:GmsDevice_1_7100_0']
    SZZX_102 = total_df[total_df.object_id == 'System1:GmsDevice_1_70001_108']
    SZZX_202 = total_df[total_df.object_id == 'System1:GmsDevice_1_70003_308']
    SZZX_301 = total_df[total_df.object_id == 'System1:GmsDevice_1_70024_408']
    SZZX_302 = total_df[total_df.object_id == 'System1:GmsDevice_1_70005_508']
    SZZX_401 = total_df[total_df.object_id == 'System1:GmsDevice_1_70006_608']
    SZZX_402 = total_df[total_df.object_id == 'System1:GmsDevice_1_70007_708']

    SZZX_701 = total_df[total_df.object_id == 'System1:GmsDevice_1_7021_2']

    # 生成5个变量相应的点阵
    SZZX_101_pot = ExtractPointFromDf_DateX(df_origin=SZZX_101, date_col='value_time', y_col='node_value')
    SZZX_102_pot = ExtractPointFromDf_DateX(df_origin=SZZX_102, date_col='value_time', y_col='node_value')
    SZZX_202_pot = ExtractPointFromDf_DateX(df_origin=SZZX_202, date_col='value_time', y_col='node_value')
    SZZX_301_pot = ExtractPointFromDf_DateX(df_origin=SZZX_301, date_col='value_time', y_col='node_value')
    SZZX_302_pot = ExtractPointFromDf_DateX(df_origin=SZZX_302, date_col='value_time', y_col='node_value')
    SZZX_401_pot = ExtractPointFromDf_DateX(df_origin=SZZX_401, date_col='value_time', y_col='node_value')
    SZZX_402_pot = ExtractPointFromDf_DateX(df_origin=SZZX_402, date_col='value_time', y_col='node_value')

    SZZX_701_pot = ExtractPointFromDf_DateX(df_origin=SZZX_701, date_col='value_time', y_col='node_value')

    data_szzx_origin = [tuple(SZZX_101_pot),
                        tuple(SZZX_102_pot),
                        tuple(SZZX_202_pot),
                        tuple(SZZX_301_pot),
                        tuple(SZZX_302_pot),
                        tuple(SZZX_401_pot),
                        tuple(SZZX_402_pot),
                        tuple(SZZX_701_pot)]

    # 定义各曲线标签
    data_name_szzx = ['试制中心-101',
                      '试制中心-102',
                      '试制中心-202',
                      '试制中心-301',
                      '试制中心-302',
                      '试制中心-401',
                      '试制中心-402',
                      '试制中心-701']

    # 处理某条线没有数据的情况，若不处理“没有数据”的情况，画线的时候会报错！
    drawing_szzx = genLPDrawing(data=data_szzx_origin, data_note=data_name_szzx, timeAxis='time', height=letter[1]*0.15)

    # 将画布添加到pdf中
    renderPDF.draw(drawing=drawing_szzx, canvas=c, x=10, y=letter[1]*0.4)

    c.showPage()

    return c

