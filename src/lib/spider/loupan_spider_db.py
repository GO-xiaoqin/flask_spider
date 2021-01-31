#!/usr/bin/env python
# coding=utf-8
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取楼盘数据的爬虫派生类
import pprint
import re
import math
import requests
import threadpool
from bs4 import BeautifulSoup
from src.lib.spider.base_spider import *
from src.lib.request.headers import *
from src.lib.utility.date import *
from src.lib.utility.db_pool import POOL
from src.lib.utility.path import *
from src.lib.utility.log import *


class LouPanBaseSpider(BaseSpider):

    def __init__(self, city, area=None, name=SPIDER_NAME):
        super(LouPanBaseSpider, self).__init__(name)
        self.city = city
        self.area = area

    def collect_city_loupan_data(self):

        t1 = time.time()  # 开始计时
        get_url = "http://{0}.fang.{1}.com/loupan/".format(self.city, self.name)
        get_url = "http://{0}.fang.{1}.com/loupan/{2}/".format(self.city, self.name, self.area) if self.area else get_url
        # 获取页面页数
        total_page = self.get_loupan_page(get_url)
        args = ["{}pg{}/".format(get_url, i) for i in range(1, int(total_page) + 1)]
        # 针对每个板块写一个文件,启动一个线程来操作
        pool_size = thread_pool_size
        pool = threadpool.ThreadPool(pool_size)
        my_requests = threadpool.makeRequests(self.get_loupan_info, args)
        [pool.putRequest(req) for req in my_requests]
        pool.wait()
        pool.dismissWorkers(pool_size, do_join=True)  # 完成后退出
        # 计时结束，统计结果
        t2 = time.time()

        return int(t2 - t1)

    @staticmethod
    def get_loupan_page(get_url):
        """
        获取抓取总页数
        :param get_url: 抓取 URL
        :return
        """
        total_page = 0
        headers = create_headers()
        try:
            response = requests.get(get_url, timeout=10, headers=headers)
        except Exception as e:
            logger.error("Have a Error {}".format(repr(e)))
            return total_page
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        # 获得总的页数
        try:
            page_box = soup.find_all('div', class_='page-box')[0]
            matches = re.search('.*data-total-count="(\d+)".*', str(page_box))
            total_page = int(math.ceil(int(matches.group(1)) / 10))
        except Exception as e:
            total_page = 1
            logger.warning("A Error {}".format(repr(e)))
        return total_page

    def get_loupan_info(self, get_url):
        """
        爬取页面获取城市新房楼盘信息
        :param get_url: 抓取 URL
        :return
        """
        houses_type = {
            '住宅': 1,
            '别墅': 2,
            '商业': 3,
            '写字楼': 4,
            '底商': 5,
        }
        houses_status = {'在售': 1, '下期待开': 2, '未开盘': 3}

        headers = create_headers()
        try:
            BaseSpider.random_delay()
            response = requests.get(get_url, timeout=10, headers=headers)
        except Exception as e:
            logger.error("Have a Error {}".format(repr(e)))
            return
        html = response.content
        soup = BeautifulSoup(html, "lxml")

        # 获得有小区信息的panel
        house_elements = soup.find_all('li', class_="resblock-list")
        for house_elem in house_elements:
            try:
                loupan = house_elem.find('a', class_='name')['title']
                resblock_status = house_elem.find('span', class_="resblock-type").text
                resblock_type = house_elem.find('div', class_="resblock-name").find_all('span')[-1].text
                resblock_location = house_elem.find('a', class_='resblock-location')['title']
                resblock_room = house_elem.find('a', class_='resblock-room').text
                resblock_tag = house_elem.find('div', class_='resblock-tag').text
                resblock_price = house_elem.find('div', class_='resblock-price').text
            except Exception as e:
                logger.error("解析程序出错!!! {}".format(repr(e)))
                continue
            # 继续清理数据
            loupan = str(loupan).strip()
            resblock_status = [houses_status[i] for i in houses_status if i in str(resblock_status).strip()]
            resblock_type = [houses_type[i] for i in houses_type if i in str(resblock_type).strip()]
            resblock_location = str(resblock_location).strip()
            resblock_room = str(resblock_room).strip().replace("\n", ",")
            resblock_tag = str(resblock_tag).strip().replace("\n", ",")
            resblock_price = str(resblock_price).strip().replace("\n\n", "\n").replace("\n", ",").replace("\xa0", "")

            # 插入到 db
            self.data_db([
                (None, loupan)[bool(loupan)],
                resblock_type[0] if resblock_type else None,
                resblock_status[0] if resblock_status else None,
                (None, resblock_location)[bool(resblock_location)],
                (None, resblock_room)[bool(resblock_room)],
                (None, resblock_tag)[bool(resblock_tag)],
                (None, resblock_price)[bool(resblock_price)],
            ])

    def data_db(self, data):
        """
        数据进入 DB;
        先查 houses_city,
        获取id 存储到houses_info
        :param data: (楼盘名字, 楼盘类型， 楼盘状态， 楼盘地址， 楼盘户型， 楼盘标签， 楼盘价格)
        ('兴盛铭仕城', '住宅', '在售', '高新区海兴路19号', '户型：,2室,/,3室,建面 76-125㎡', '小户型,VR看房,近主干道,现房', '11500,元/㎡(均价)
        :return:
        """
        # 获取 mysql 连接
        coon = POOL.connection()
        cur = coon.cursor()
        sql = """select * from houses_city_ke where houses=%s and area_code=%s and city_code=%s"""
        cur.execute(sql, [('', data[0])[bool(data[0])], ('', self.area)[bool(self.area)], self.city])
        result = cur.fetchone()
        if result:
            houses_id = result[0]
        else:
            try:
                cur.execute(
                    """insert into houses_city_ke(houses, area_code, city_code) VALUES (%s, %s, %s)""",
                    [('', data[0])[bool(data[0])], ('', self.area)[bool(self.area)], self.city]
                )
                coon.commit()
            except Exception as e:
                logger.error(repr(e))
                logger.error("获取 houses_id 失败!!!")
                coon.rollback()
                cur.close()
                coon.close()
                return
            else:
                cur.execute(sql, [('', data[0])[bool(data[0])], ('', self.area)[bool(self.area)], self.city])
                result = cur.fetchone()
                houses_id = result[0]

        # 获取到 houses_id 进行存储
        try:
            data.append(int(houses_id))
            cur.execute(
                """
                insert into houses_info_ke(
                houses_title, houses_type, houses_status, houses_location, houses_room,
                houses_tag, houses_price, houses_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                data
            )
            coon.commit()
        except Exception as e:
            logger.error(repr(e))
            logger.error("存储 houses_info 失败!!!")
            coon.rollback()
        else:
            logger.info("存储 houses {} 成功 by in houses_id {}".format(data[0], houses_id))
        finally:
            cur.close()
            coon.close()
            return

    def start(self):
        """
        楼盘爬虫启动程序
        :return:
        """
        logger.info("准备抓取 {} {}".format(self.city, self.area))

        try:
            result = self.collect_city_loupan_data()    # 返回运行时间
        except Exception as e:
            logger.error(repr(e))
            result = 0

        logger.info("Total cost {0} second".format(result))

        return result


if __name__ == '__main__':
    spider = LouPanBaseSpider('tr', 'bijiangqu')
    spider.start()
