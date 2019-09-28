# -*- coding:utf-8 -*-
__author__ = 'gxb'
'''
分析国庆期间国人旅游景点热点地区
'''

import requests
import json
import os
import pandas
import time
import random


PLACES_EXCEL_PATH = '去哪儿国庆景点.xlsx'


def spider_places(kw, page):
    '''
    获取单页的数据信息
    :param kw:
    :param page:
    :return:
    '''
    page_json_url = f'https://piao.qunar.com/ticket/list.json?keyword={kw}&page={page}'
    print('开始爬取url：' + page_json_url)
    headers = {
        'referer': 'https://piao.qunar.com/ticket/list.htm?keyword=%E5%9B%BD%E5%BA%86%E6%99%AF%E7%82%B9&page=3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    try:
        response = requests.get(page_json_url, headers=headers)
        response.raise_for_status()
        response_json = json.loads(response.text)
        sightList_json = response_json['data']['sightList']
        if sightList_json:
            # 获取结果集合list
            places_list = get_place_info(sightList_json)
            # 将结果保存到excel中
            save_as_excel(places_list)
            return True
        else:
            return False
    except Exception as e:
        raise e


def get_place_info(sightList_json):
    '''
    解析景点信息，封装为 list返回
    :param sightList_json:
    :return:
    '''
    places_list = []
    for sight in sightList_json:
        # 如果不存在某个key，使用sight['key']就会抛出keyError异常，所以使用dict.get(key, default=None)
        # key - 字典中要查找的键; default - 如果指定键的值不存在时，返回该默认值。
        place_info = {
            'id': sight['sightId'],  # id
            'name': sight['sightName'],  # 名称
            'star': sight.get('star', '无'),  # 星级
            'free': sight.get('free', '无'),  # 是否免费
            'score': sight.get('score', 0),  # 评分
            'point': sight.get('point', '0,0'),  # 坐标
            'address': sight.get('address', '无'),  # 地址
            'districts': sight.get('districts', '无'),  # 区域（省-市-县）
            'saleCount': sight.get('saleCount', 0),  # 销量
            'qunarPrice': sight.get('qunarPrice', 0)  # 去哪儿价格
        }
        places_list.append(place_info)
    print('解析得到数据集合如下：')
    print(places_list)
    return places_list


def save_as_excel(places_list):
    '''
    将数据保存到excle表中
    :param places_list:
    :return:
    '''
    if os.path.exists(PLACES_EXCEL_PATH):
        df = pandas.read_excel(PLACES_EXCEL_PATH)
        df = df.append(places_list)
    else:
        df = pandas.DataFrame(places_list)
    writer = pandas.ExcelWriter(PLACES_EXCEL_PATH)
    df.to_excel(excel_writer=writer,
                columns=['id', 'name', 'star', 'free', 'score', 'point', 'address', 'districts', 'saleCount',
                         'qunarPrice'],
                encoding='utf-8', sheet_name='去哪儿旅游景点综合数据', index=False)
    writer.save()
    writer.close()
    print('保存到excel完成')


def batch_spider(keyword):
    '''
    分页爬取数据信息，如果无法获取信息则停止
    :param keyword:
    :return:
    '''
    # 首先清空数据
    if os.path.exists(PLACES_EXCEL_PATH):
        os.remove(PLACES_EXCEL_PATH)

    # 批量爬取
    index = 1
    while spider_places(keyword, index):
        print('开始爬取一次数据')
        index += 1
        time.sleep(random.random() * 3)
    print('爬取完毕')


if __name__ == '__main__':
    # 根据关键字爬取数据
    batch_spider('国庆景点')
