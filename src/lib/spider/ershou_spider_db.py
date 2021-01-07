#!/usr/bin/env python
# coding=utf-8
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取二手房数据的爬虫派生类

import re
import threadpool
from bs4 import BeautifulSoup
from src.lib.item.ershou import *
from src.lib.zone.city import get_city
from src.lib.spider.base_spider import *
from src.lib.utility.date import *
from src.lib.utility.path import *
from src.lib.zone.area import *
from src.lib.utility.log import *
import src.lib.utility.version


class ErShouSpider(BaseSpider):
    def __init__(self, city, area=None, name=SPIDER_NAME):
        super(ErShouSpider, self).__init__(name)
        self.city = city
        self.area = area

    def collect_area_ershou_data(self):

        t1 = time.time()  # 开始计时
        get_url = "http://{0}.{1}.com/ershoufang/".format(self.city, self.name)
        get_url = "http://{0}.{1}.com/ershoufang/{2}/".format(self.city, self.name, self.area) if self.area else get_url
        # 获取页面页数
        total_page = self.get_ershou_page(get_url)
        args = ["{}pg{}/".format(get_url, i) for i in range(1, int(total_page) + 1)]

        # 针对每个板块写一个文件,启动一个线程来操作
        pool_size = thread_pool_size
        pool = threadpool.ThreadPool(pool_size)
        my_requests = threadpool.makeRequests(self.get_area_ershou_info, args)
        [pool.putRequest(req) for req in my_requests]  # debug 调试 my_requests[:1]
        pool.wait()
        pool.dismissWorkers(pool_size, do_join=True)  # 完成后退出

        # 计时结束，统计结果
        t2 = time.time()

        return int(t2 - t1)

    @staticmethod
    def get_ershou_page(get_url):
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
            matches = re.search('.*"totalPage":(\d+),.*', str(page_box))
            total_page = int(matches.group(1))
        except Exception as e:
            total_page = 1
            logger.warning("A Error {}".format(repr(e)))
        return total_page

    def get_area_ershou_info(self, get_url):
        """
        通过爬取页面获得城市指定版块的二手房信息
        """
        headers = create_headers()
        try:
            BaseSpider.random_delay()
            response = requests.get(get_url, timeout=10, headers=headers)
        except Exception as e:
            logger.error("Have a Error {}".format(repr(e)))
            return
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        # TODO 进行数据清晰获取
        # 获得有小区信息的panel
        house_elements = soup.find_all('li', class_="clear")
        for house_elem in house_elements:
            price = house_elem.find('div', class_="totalPrice")
            name = house_elem.find('div', class_='title')
            desc = house_elem.find('div', class_="houseInfo")
            pic = house_elem.find('a', class_="img").find('img', class_="lj-lazy")

            # 继续清理数据
            price = price.text.strip()
            name = name.text.replace("\n", "")
            desc = desc.text.replace("\n", "").strip()
            pic = pic.get('data-original').strip()
            # print(pic)

    def start(self):
        """
        楼盘爬虫启动程序
        :return:
        """
        logger.info("准备抓取 {} {}".format(self.city, self.area))
        try:
            result = self.collect_area_ershou_data()    # 返回运行时间
        except Exception as e:
            logger.error(repr(e))
            result = 0

        logger.info("Total cost {0} second".format(result))

        return result


if __name__ == '__main__':
    spider = ErShouSpider("gz", "shunde")
    spider.start()
