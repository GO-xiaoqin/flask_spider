#!/usr/bin/env python
# coding=utf-8
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取二手房数据的爬虫派生类

import re
import threadpool
from bs4 import BeautifulSoup
from src.lib.item.ershou import *
from src.lib.utility.db_pool import POOL
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
        # 获得有小区信息的panel
        house_elements = soup.find_all('li', class_="clear")
        for house_elem in house_elements:
            try:
                name = house_elem.find('div', class_='title').find('a')['title']
                positioninfo = house_elem.find('div', class_="positionInfo").text
                houseinfo = house_elem.find('div', class_="houseInfo").text
                followinfo = house_elem.find('div', class_="followInfo").text
                tag = house_elem.find('div', class_="tag").text
                priceinfo = house_elem.find('div', class_="priceInfo").text
            except Exception as e:
                logger.error("解析程序出错!!! {}".format(repr(e)))
                continue
            # 继续清理数据
            name = str(name).strip()
            positioninfo = str(positioninfo).strip()
            houseinfo = str(houseinfo).strip().replace("\n", ",").replace(" ", "")
            followinfo = str(followinfo).strip().replace("\n", ",").replace(" ", "")
            tag = str(tag).strip().replace("\n", ",")
            priceinfo = str(priceinfo).strip().replace("\n\n", ",").replace("\n", ",")
            # logger.info((name, positioninfo, houseinfo, followinfo, tag, priceinfo))
            # 插入到 db
            self.data_db([
                (None, name)[bool(name)],
                (None, positioninfo)[bool(positioninfo)],
                (None, houseinfo)[bool(houseinfo)],
                (None, followinfo)[bool(followinfo)],
                (None, tag)[bool(tag)],
                (None, priceinfo)[bool(priceinfo)],
            ])

    def data_db(self, data):
        """
        数据进入 DB;
        先查 houses_city,
        获取id 存储到ershou_info
        :param data: (楼房名字, 地址信息， 具体信息， 关注信息， 标签， 价格)
        ('碧桂园中北区 实用三房 低楼层 方便看房', '顺德碧桂园中北区（洋房）',
        '低楼层,(共6层),|1992年建|,3室2厅|81.6平米,|北',
        '8人关注,/1月前发布',
        '满两年,VR看装修,随时看房',
        '117万,单价14339元/平米')
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
                insert into ershou_info_ke (ershou_name, positioninfo, houseinfo, followinfo, tag, priceinfo, houses_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                data
            )
            coon.commit()
        except Exception as e:
            logger.error(repr(e))
            logger.error("存储 xiaoqu_info 失败!!!")
            coon.rollback()
        else:
            logger.info("存储 xiaoqu {} 成功 by in houses_id {}".format(data[0], houses_id))
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
            result = self.collect_area_ershou_data()    # 返回运行时间
        except Exception as e:
            logger.error(repr(e))
            result = 0

        logger.info("Total cost {0} second".format(result))

        return result


if __name__ == '__main__':
    spider = ErShouSpider("gz")
    spider.start()
