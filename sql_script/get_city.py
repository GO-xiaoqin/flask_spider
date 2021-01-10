# coding=utf-8
import re

import requests
import pprint
from urllib import parse
from lxml import etree
import pymysql


def main():
    url = "https://www.ke.com/city/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/87.0.4280.88 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    response = requests.get(url, headers=headers)
    city_dict = dict()
    if response.status_code == 200:
        html = etree.HTML(response.text)
        citys_data = html.xpath('//*[contains(@class,"city-item")]//*[@class="city_province"]')
        for i in citys_data:

            try:
                a_l = [parse.urljoin(url, i) for i in i.xpath('.//ul/li/a/@href')]
                a_stauts = [(1, 0)['fang' in i] for i in i.xpath('.//ul/li/a/@href')]
                code = [re.findall(r'\/\/(.*?)\.', i)[0] if re.findall(r'\/\/(.*?)\.', i) else i for i in i.xpath('.//ul/li/a/@href')]
                city_code = zip(i.xpath('.//ul/li//text()'), code, a_l, a_stauts)
            except Exception:
                continue

            city_dict[str(i.xpath('.//*[contains(@class,"city_list_tit")]//text()')[0]).strip()] = list(city_code)

        # pprint.pprint(city_dict)
        db = pymysql.connect("localhost", "root", "xu551212", "test")
        cursor = db.cursor()
        sql = "INSERT INTO provice_city_ke (city, city_code, city_href, city_status, provice) VALUES (%s,%s,%s,%s,%s)"

        val = list()
        for i in city_dict:
            for j in city_dict[i]:
                val.append((j[0], j[1], j[2], j[3], i))
        try:
            # 执行sql语句
            cursor.executemany(sql, val)
            # 提交到数据库执行
            db.commit()
        except Exception as e:
            print("有错误!!! {}".format(repr(e)))
            # 如果发生错误则回滚
            db.rollback()
        else:
            print("保存成功！！！")

        # 关闭数据库连接
        db.close()


if __name__ == "__main__":
    main()
