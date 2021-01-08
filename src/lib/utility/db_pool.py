#!/usr/bin/env python
# coding=utf-8

import pymysql
from dbutils.pooled_db import PooledDB
from src.lib.utility.log import logger

POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
    maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
    maxshared=1,  # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    ping=0,
    # ping MySQL服务端，检查是否服务可用。
    # 如：0 = None = never,
    # 1 = default = whenever it is requested,
    # 2 = when a cursor is created,
    # 4 = when a query is executed,
    # 7 = always
    host='127.0.0.1',
    port=3306,
    user='liu',
    password='9090',
    database='test',
    charset='utf8'
)


def get_area_city():
    """
    获取数据库中楼盘在每个城市的区域
    :return:
    """
    # 获取 mysql 连接
    coon = POOL.connection()
    cur = coon.cursor()
    sql_fang = """
        select a.area,a.area_code, b.city, b.city_code, b.provice from area_city_ke a 
        join provice_city_ke b on a.city_id=b.id
    """
    sql_ershou = """
        select a.area,a.area_code, b.city, b.city_code, b.provice from ershou_area_ke a 
        join provice_city_ke b on a.city_id=b.id
    """
    try:
        cur.execute(sql_fang)
        result_fang = cur.fetchall()
        cur.execute(sql_ershou)
        result_ershou = cur.fetchall()

        result = {
            'result_fang': result_fang,
            'result_ershou': result_ershou,
        }

        for r in result:
            result_city = {i[3]: i[2] for i in result[r]}
            result_city = [{'city_name': result_city[i], 'city_code': i, 'area': []} for i in result_city]
            result_ = [{'name': i, 'city': []} for i in set([i[4] for i in result[r]])]

            for i in result[r]:
                for j in range(len(result_city)):
                    if i[3] in result_city[j]['city_code']:
                        result_city[j]['area'].append({'area_name': i[0], 'area_code': i[1]})
                        result_city[j]['provice'] = i[4]
            for i in result_city:
                for j in range(len(result_)):
                    if i['provice'] == result_[j]['name']:
                        result_[j]['city'].append(i)
            result[r] = result_

    except Exception as e:
        logger.error(repr(e))
        result = dict()
    finally:
        cur.close()
        coon.close()
    return result


if __name__ == '__main__':
    print(get_area_city())
