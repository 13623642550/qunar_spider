# -*- coding:utf-8 -*-
__author__ = 'gxb'
'''
去哪儿网数据分析
'''

import numpy
import pandas
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Map

# 读取excel数据
DF = pandas.read_excel('去哪儿国庆景点.xlsx')


def gen_place_sale_bar():
    '''
    生成景点门票销量分析柱状图
    :return:
    '''
    df = DF.copy()
    # 1.生成一个名称和数量的透视表
    place_sale = df.pivot_table(index='name', values='saleCount')
    # 2.根据销量进行排序
    # inplace - 是否用排序后的数据集替换原来的数据，默认为False，即不替换; ascending - 是否按指定列的数组升序排列，默认为True，即升序排列;
    place_sale.sort_values('saleCount', inplace=True, ascending=True)
    # 3.生成柱状图
    place_sale_bar = (
        Bar()
            .add_xaxis(place_sale.index.to_list()[-20:])
            .add_yaxis('', list(map(int, numpy.ravel(place_sale.values)))[-20:])
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position='right'))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='国庆旅游热门景点门票销量TOP20'),
            yaxis_opts=opts.AxisOpts(name='景点名称'),
            xaxis_opts=opts.AxisOpts(name='门票销量')
        )
    )
    place_sale_bar.render('景区门票销量柱状图.html')
    print('柱状图生成完毕')


def gen_place_sale_amount_bar():
    '''
    分析景区销售的票价排行
    :return:
    '''
    df = DF.copy()
    # 计算：总金额=价格*销量
    amount_list = []
    for index, row in df.iterrows():
        amount = row['qunarPrice'] * row['saleCount']
        amount_list.append(amount)
    # 将金额数据加入表格中
    df['amount'] = amount_list
    # 生成一个名称和销售金额的透视表
    place_amount = df.pivot_table(index='name', values='amount')
    # 根据销售额排序
    place_amount.sort_values('amount', inplace=True, ascending=True)
    # 生成柱状图
    place_amount_bar = (
        Bar()
            .add_xaxis(place_amount.index.tolist()[-20:])
            .add_yaxis('', list(map(int, numpy.ravel(place_amount.values)))[-20:])
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position='right'))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='国庆旅游热门景点门票销售额TOP20'),
            yaxis_opts=opts.AxisOpts(name='景点名称'),
            xaxis_opts=opts.AxisOpts(name='门票销售额')
        )
    )
    place_amount_bar.render('景点门票销售额TOP20柱状图.html')
    print('景点门票销售额TOP20柱状图生成完毕')


def gen_star_amount_pie():
    '''
    生成景区星级占比情况分析图（饼状图）
    :return:
    '''
    df = DF.copy()
    start_count_list = for_datas_to_list(df['star'])
    # 生成二维数组
    star_count_list = [list(z) for z in zip(start_count_list.keys(), start_count_list.values())]
    print('*' * 50)
    print(star_count_list)
    pie = (
        Pie()
            .add('', star_count_list)
            .set_global_opts(title_opts=opts.TitleOpts(title='景区星级比例'))
            .set_series_opts(label_opts=opts.LabelOpts(formatter='{b}: {c}'))
    )
    pie.render('景区星级分布比例饼状图.html')
    print('景区星级分布比例饼状图生成完毕')


def gen_hot_map():
    '''
    生成各省份景区数量热力分布图
    :return:
    '''
    df = DF.copy()
    # 将所有的省市信息解析，然后存入新的序列series中，交给for_datas_to_list函数去解析
    new_list = []
    for i in df['districts']:
        new_list.append(i.split('·')[0])
    new_series = pandas.Series(new_list)
    # 生成各省份对应的数量
    count_dict = for_datas_to_list(new_series)
    # 获取其中数量最多的数值
    max_value = count_dict.get(max(count_dict, key=count_dict.get))
    print('最大的数字为==>' + str(max_value))
    province_count_list = [list(z) for z in zip(count_dict.keys(), count_dict.values())]
    # 制作热力图
    map = (
        Map()
            .add('各省份旅游景点分布热力图', province_count_list, 'china')
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(max_=max_value)
        )
    )
    map.render('各省份旅游景点分布热力图.html')
    print('各省份旅游景点分布热力图生成完毕')


def for_datas_to_list(column_data):
    '''
    将读取的列数据相同元素合并为并返回其数量
    :param column_data:
    :return:
    '''
    # 首先循环读取所有的星级类型，将所有值设为0存入字典
    result_list = {i: 0 for i in column_data}
    for data in column_data:
        result_list[data] = result_list.get(data) + 1
    return result_list


def gen_recommend_bar():
    '''
    生成推荐景点分析柱状图
    :return:
    '''
    df = DF.copy()
    recommend_list = []
    for index, row in df.iterrows():
        # 简单推荐算法：推荐系数=评分/(销量*价格) * 1000
        try:
            recommend = (row['score'] * 1000) / (row['saleCount'] * row['qunarPrice'])
        except ZeroDivisionError:
            recommend = 0
        recommend_list.append(recommend)
    df['recommend'] = recommend_list
    # 生成透视表
    place_recommend = df.pivot_table(index='name', values='recommend')
    # 按照推荐系数升序排列
    place_recommend.sort_values('recommend', inplace=True, ascending=True)
    # 生成柱状图
    place_recommend_bar = (
        Bar()
            .add_xaxis(place_recommend.index.tolist()[-20:])
            .add_yaxis('', list(map(int, numpy.ravel(place_recommend.values)))[-20:])
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position='right'))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='国庆旅游热门景点推荐排行'),
            yaxis_opts=opts.AxisOpts(name='景点名称'),
            xaxis_opts=opts.AxisOpts(name='推荐系数')
        )
    )
    place_recommend_bar.render('国庆旅游热门景点推荐排行.html')
    print('国庆旅游热门景点推荐排行生成完毕')


if __name__ == '__main__':
    # 1.景区门票销量排行分析（柱状图）
    gen_place_sale_bar()
    # 2.景点门票销售额排行分析（柱状图）
    gen_place_sale_amount_bar()
    # 3.景点销量热力图分析（地图）
    gen_hot_map()
    # 4.推荐景点分析（柱状图）
    gen_recommend_bar()
    # 5.景区星级占比分析（饼状图）
    gen_star_amount_pie()
