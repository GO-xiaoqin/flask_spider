# coding=utf-8

import requests
import threadpool
import pymysql
from lxml import etree
from conf import *
from src.lib.spider.base_spider import thread_pool_size


db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PWD, MYSQL_DB)

url = "http://{}.ke.com/xiaoqu/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}


def main(city, city_id):
    db2 = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PWD, MYSQL_DB)
    try:
        response = requests.get(url.format(city), headers=headers, timeout=10)
    except Exception as e:
        print(repr(e))
    else:
        if response.status_code == 200:
            html = etree.HTML(response.text)
            citys_data = html.xpath('//*[@class="position"]//a[contains(@class,"CLICKDATA")]')
            for i in citys_data:
                cursor = db2.cursor()
                cursor.execute("SELECT * FROM ershou_area_ke WHERE area=%s", [i.xpath('./text()')[0]])
                if cursor.fetchone():
                    cursor.close()
                    continue
                try:
                    area_code = [j for i in i.xpath('./@href') for j in str(i).split('/') if j and j != 'xiaoqu'][0]
                    sql = "INSERT INTO ershou_area_ke(area, area_code, city_id) VALUES (%s,%s,%s)"
                    # 执行sql语句
                    cursor.execute(sql, (i.xpath('./text()')[0], area_code, int(city_id)))
                    # 提交到数据库执行
                    db2.commit()
                except Exception as e:
                    print("有错误!!! {}".format(repr(e)))
                    print(i.xpath('./text()'), i.xpath('./@href'), int(city_id))
                    # 如果发生错误则回滚
                    db2.rollback()
                else:
                    print("保存成功！！！")

                cursor.close()
            # 关闭数据库连接
            db2.close()


if __name__ == "__main__":
    # 获取城市
    cursor = db.cursor()
    cursor.execute("SELECT * FROM provice_city_ke where city_status=1")
    city_data = cursor.fetchall()
    # 关闭游标和数据库的连接
    cursor.close()
    # 关闭数据库连接
    db.close()

    nones = [None for i in range(len(city_data))]
    city = [i[2] for i in city_data]
    city_id = [i[0] for i in city_data]

    arges = zip(zip(city, city_id), nones)

    # 针对每个板块写一个文件,启动一个线程来操作
    pool_size = thread_pool_size
    pool = threadpool.ThreadPool(pool_size)
    my_requests = threadpool.makeRequests(main, arges)
    [pool.putRequest(req) for req in my_requests]   # debug 调试 my_requests[:1]
    pool.wait()
    pool.dismissWorkers(pool_size, do_join=True)  # 完成后退出

