#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取楼盘数据的爬虫派生类
import pprint
import re
import math
import requests
from bs4 import BeautifulSoup
from src.lib.item.loupan import *
from src.lib.spider.base_spider import *
from src.lib.request.headers import *
from src.lib.utility.date import *
from src.lib.utility.path import *
from src.lib.zone.city import get_city
from src.lib.utility.log import *
import src.lib.utility.version


class LouPanBaseSpider(BaseSpider):
    def collect_city_loupan_data(self, city_name, area=None):
        """
        将指定城市的新房楼盘数据存储下来，默认存为csv文件
        :param area: 城市的区域
        :param city_name: 城市
        :return: None
        """
        t1 = time.time()  # 开始计时
        get_url = "http://{0}.fang.{1}.com/loupan/".format(city_name, SPIDER_NAME)
        get_url = "http://{0}.fang.{1}.com/loupan/{2}/".format(city_name, SPIDER_NAME, area) if area else get_url
        # 获取页面页数
        total_page = self.get_loupan_page(get_url)
        logger.info(total_page)
        # TODO 以获取到页数添加线程池进行抓取


        # # 开始获得需要的板块数据
        # loupans = self.get_loupan_info(get_url)
        # logger.info(loupans)

        # csv_file = self.today_path + "/{0}.csv".format(city_name)
        # with open(csv_file, "w") as f:
        #     # 开始获得需要的板块数据
        #     loupans = self.get_loupan_info(city_name)
        #     self.total_num = len(loupans)
        #     if fmt == "csv":
        #         for loupan in loupans:
        #             f.write(self.date_string + "," + loupan.text() + "\n")



        # self.total_num = len(loupans)
        # pprint.pprint(loupans)
        # print(self.total_num)

        return

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


    @staticmethod
    def get_loupan_info(get_url):
        """
        爬取页面获取城市新房楼盘信息
        :param get_url: 抓取 URL
        :return
        """
        loupan_list = list()
        headers = create_headers()
        try:
            response = requests.get(get_url, timeout=10, headers=headers)
        except Exception as e:
            logger.error("Have a Error {}".format(repr(e)))
            return loupan_list
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
            resblock_status = str(resblock_status).strip()
            resblock_type = str(resblock_type).strip()
            resblock_location = str(resblock_location).strip()
            resblock_room = str(resblock_room).strip().replace("\n", ",")
            resblock_tag = str(resblock_tag).strip().replace("\n", ",")
            resblock_price = str(resblock_price).strip().replace("\n\n", "\n").replace("\n", ",").replace("\xa0", "")

            loupan_list.append((
                (0, loupan)[bool(loupan)],
                (0, resblock_type)[bool(resblock_type)],
                (0, resblock_status)[bool(resblock_status)],
                (0, resblock_location)[bool(resblock_location)],
                (0, resblock_room)[bool(resblock_room)],
                (0, resblock_tag)[bool(resblock_tag)],
                (0, resblock_price)[bool(resblock_price)],
            ))
        return loupan_list

    def start(self, city, area=None):
        """
        楼盘爬虫启动程序
        :param city:
        :param area:
        :return:
        """
        logger.info("准备抓取 {} {}".format(city, area))
        result = self.collect_city_loupan_data(city, area)

        # logger.info('Today date is: %s' % self.date_string)
        # self.today_path = create_date_path("{0}/loupan".format(SPIDER_NAME), city, self.date_string)
        #
        # t1 = time.time()  # 开始计时
        # self.collect_city_loupan_data(city)
        # t2 = time.time()  # 计时结束，统计结果
        #
        # logger.info("Total crawl {0} loupan.".format(self.total_num))
        # print("Total cost {0} second ".format(t2 - t1))


if __name__ == '__main__':
    spider = LouPanBaseSpider()
    spider.start('bj')
