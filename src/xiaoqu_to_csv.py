#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# read data from csv, write to database
# database includes: mysql/mongodb/excel/json/csv

import os
from src.lib.utility.path import DATA_PATH
from src.lib.zone.city import *
from src.lib.utility.date import *
from src.lib.spider.base_spider import SPIDER_NAME


def xiaoqu_to_csv(data):
    """

    :param data: (city, house_type)
    :return:
    """
    city = data[0]
    # 准备日期信息，爬到的数据存放到日期相关文件夹下
    date = get_date_string()
    # 获得 csv 文件路径
    # date = "20180331"   # 指定采集数据的日期
    # city = "sh"         # 指定采集数据的城市
    csv_dir = "{0}/{1}/{2}/{3}/{4}".format(DATA_PATH, SPIDER_NAME, data[1], city, date)
    csv_path = csv_dir + "{}_{}.csv".format(data[1], city)
    csv_file = open(csv_path, "w")
    line = "{0};{1};{2};{3};{4};{5};{6}\n".format('city_ch', 'date', 'district', 'area', 'xiaoqu', 'price', 'sale')
    csv_file.write(line)
    city_ch = get_chinese_city(city)
    files = list()
    if not os.path.exists(csv_dir):
        print("{0} does not exist.".format(csv_dir))
        print("Please run 'python xiaoqu.py' firstly.")
        print("Bye.")
        exit(0)
    else:
        print('OK, start to process ' + get_chinese_city(city))
    for csv in os.listdir(csv_dir):
        data_csv = csv_dir + "/" + csv
        # print(data_csv)
        files.append(data_csv)

    # 清理数据
    count = 0
    for csv in files:
        with open(csv, 'r') as f:
            for line in f:
                print(line)
                count += 1
                text = line.strip()
                try:
                    # 如果小区名里面没有逗号，那么总共是6项
                    if text.count(',') == 5:
                        date, district, area, xiaoqu, price, sale = text.split(',')
                    elif text.count(',') < 5:
                        continue
                    else:
                        fields = text.split(',')
                        date = fields[0]
                        district = fields[1]
                        area = fields[2]
                        xiaoqu = ','.join(fields[3:-2])
                        price = fields[-2]
                        sale = fields[-1]
                except Exception as e:
                    print(text)
                    print(e)
                    continue
                print("{0} {1} {2} {3} {4} {5}".format(date, district, area, xiaoqu, price, sale))
                sale = sale.replace(r'套在售二手房', '')
                price = price.replace(r'暂无', '0')
                price = price.replace(r'元/m2', '')
                price = int(price)
                sale = int(sale)
                line = "{0};{1};{2};{3};{4};{5};{6}\n".format(city_ch, date, district, area, xiaoqu, price, sale)
                csv_file.write(line)

    # 写入，并且关闭句柄
    csv_file.close()

    print("Total write {0} items to database.".format(count))
    return csv_path


if __name__ == '__main__':
    xiaoqu_to_csv(('cd', 'xiaoqu'))
