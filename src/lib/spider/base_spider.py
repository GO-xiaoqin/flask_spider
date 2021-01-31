#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬虫基类
# 爬虫名常量，用来设置爬取哪个站点

import threading
from src.lib.utility.date import *
import random

thread_pool_size = 50

# 防止爬虫被禁，随机延迟设定
# 如果不想delay，就设定False，
# 具体时间可以修改random_delay()，由于多线程，建议数值大于10
RANDOM_DELAY = False
LIANJIA_SPIDER = "lianjia"
BEIKE_SPIDER = "ke"
SPIDER_NAME = BEIKE_SPIDER


class BaseSpider(object):
    @staticmethod
    def random_delay():
        if RANDOM_DELAY:
            time.sleep(random.randint(0, 16))

    def __init__(self, name=SPIDER_NAME):
        self.name = name
        # 准备日期信息，爬到的数据存放到日期相关文件夹下
        self.date_string = get_date_string()

        self.total_num = 0  # 总的小区个数，用于统计
        self.mutex = threading.Lock()  # 创建锁

