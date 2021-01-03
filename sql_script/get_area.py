# coding=utf-8
import re

import requests
import pprint
from lxml import etree
import pymysql


def main():
    # 获取城市
    db = pymysql.connect("localhost", "root", "xu551212", "test")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM provice_city")
    city_data = cursor.fetchall()
    # 关闭游标和数据库的连接
    cursor.close()
    print(city_data)

    url = "http://{}.fang.ke.com/loupan/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/87.0.4280.88 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    for j in range(len(city_data)):
        print("进度:{0}%".format(round((j + 1) * 100 / len(city_data))), end="\r", flush=True)
        try:
            response = requests.get(url.format(city_data[j][2]), headers=headers, timeout=10)
        except Exception as e:
            print(repr(e))
        else:
            if response.status_code == 200:
                html = etree.HTML(response.text)
                citys_data = html.xpath('//*[@class="district-wrapper"]//*[@class="district-item"] | //*[@class="items district"]//li')
                for i in citys_data:
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM area_city WHERE area=%s", (i.xpath('./text()')[0]))
                    if cursor.fetchone():
                        cursor.close()
                        continue
                    sql = "INSERT INTO area_city(area, area_code, city_id) VALUES (%s,%s,%s)"
                    try:
                        # 执行sql语句
                        cursor.execute(sql, (i.xpath('./text()')[0], i.xpath('./@data-district-spell')[0], city_data[j][0]))
                        # 提交到数据库执行
                        db.commit()
                    except Exception as e:
                        print("有错误!!! {}".format(repr(e)))
                        print(i.xpath('./text()')[0], i.xpath('./@data-district-spell')[0], city_data[j][0])
                        # 如果发生错误则回滚
                        db.rollback()
                    else:
                        print("保存成功！！！")
                    finally:
                        cursor.close()

    # 关闭数据库连接
    db.close()


if __name__ == "__main__":
    main()
