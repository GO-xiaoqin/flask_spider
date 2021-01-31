#!/usr/bin/env python
# coding=utf-8
# 此代码仅供学习与交流，请勿用于商业用途。
import requests
from bs4 import BeautifulSoup

from src.lib.request.headers import create_headers
from src.lib.spider.base_spider import BaseSpider
from src.lib.utility.db_pool import get_ch_city, get_ch_area, POOL
from src.lib.utility.log import logger
from src.lib.utility.reverse_geocoding import getlnglat


def get_info_spider(url, area, city, houses_type):
    """
    获取小区具体信息的spider
    :param url:
    :param area:
    :param city:
    :return:
    """
    headers = create_headers()
    try:
        BaseSpider.random_delay()
        response = requests.get(url, timeout=10, headers=headers)
    except Exception as e:
        logger.error("Have a Error {}".format(repr(e)))
        return

    html = response.text
    soup = BeautifulSoup(html, "lxml")
    try:
        xiaoqu_title = soup.find('h1', class_='main')['title']
        xiaoquinfo = soup.find_all('div', class_='xiaoquInfoItem')
        building_type = xiaoquinfo[0].text
        property_expenses = xiaoquinfo[1].text
        property_company = xiaoquinfo[2].text
        developer = xiaoquinfo[3].text
        total_number_of_buildings = xiaoquinfo[4].text
        total_number_of_houses = xiaoquinfo[5].text
        nearby_stores = xiaoquinfo[6].text
    except Exception as e:
        logger.error(repr(e))
        return
    if xiaoqu_title:    # 获取到小区名字后接着获取小区其他信息
        xiaoqu_title = xiaoqu_title
        building_type = str(building_type).strip().replace("\n", ",")
        property_expenses = str(property_expenses).strip().replace("\n\n", ",").replace(" ", "")
        property_company = str(property_company).strip().replace("\n", ",")
        developer = str(developer).strip().replace("\n", ",")
        total_number_of_buildings = str(total_number_of_buildings).strip().replace("\n", ",")
        total_number_of_houses = str(total_number_of_houses).strip().replace("\n", ",")
        nearby_stores = str(nearby_stores).strip().replace("\n\n", ",")
        # 获取经纬度
        city = get_ch_city(city)
        area = get_ch_area(area, houses_type)
        if city and area:
            address = city[0] + area[0] + xiaoqu_title
            lat, lng = getlnglat(address, city[0])

            # 获取 mysql 连接
            coon = POOL.connection()
            cur = coon.cursor()
            sql = """select * from xiaoqu_detail_ke where xiaoqu_title=%s"""
            cur.execute(sql, xiaoqu_title)
            result = cur.fetchone()
            if result:
                xiaoqu_id = result[0]
            else:
                try:
                    cur.execute(
                        """
                        insert into xiaoqu_detail_ke(
                        xiaoqu_title,
                        building_type,
                        property_expenses,
                        property_company,
                        developer,
                        total_number_of_buildings,
                        total_number_of_houses,
                        nearby_stores,
                        lat,
                        lng) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            xiaoqu_title,
                            ('', building_type)[bool(building_type)],
                            ('', property_expenses)[bool(property_expenses)],
                            ('', property_company)[bool(property_company)],
                            ('', developer)[bool(developer)],
                            ('', total_number_of_buildings)[bool(total_number_of_buildings)],
                            ('', total_number_of_houses)[bool(total_number_of_houses)],
                            ('', nearby_stores)[bool(nearby_stores)],
                            ('', lat)[bool(lat)],
                            ('', lng)[bool(lng)],
                        ]
                    )
                    coon.commit()
                except Exception as e:
                    logger.error(repr(e))
                    coon.rollback()
                    cur.close()
                    coon.close()
                    return
                else:
                    cur.execute(sql, xiaoqu_title)
                    result = cur.fetchone()
                    xiaoqu_id = result[0]
            cur.close()
            coon.close()
            return xiaoqu_id


if __name__ == '__main__':
    get_info_spider('https://sh.ke.com/xiaoqu/5011000001265/?fb_expo_id=408232304537346073',  'songjiang', 'sh', 'ershou')
