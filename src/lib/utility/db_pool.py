#!/usr/bin/env python
# coding=utf-8

import pymysql
from dbutils.pooled_db import PooledDB
from src.lib.utility.log import logger
from conf import *

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
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PWD,
    database=MYSQL_DB,
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


def get_crawl_task(house_type, city, area):
    """
    获取数据库中抓取任务
    :return:
    """
    # 获取 mysql 连接
    coon = POOL.connection()
    cur = coon.cursor()
    sql = """
        select * from crawl_task where house_type=%s and city=%s and area=%s and crawl_time is not null 
        and to_days(createtime)=to_days(now())
    """
    try:
        cur.execute(sql, (house_type, city, area))
        result = cur.fetchall()
    except Exception as e:
        logger.error(repr(e))
        result = None
    finally:
        cur.close()
        coon.close()
    return result


def insert_crawl_task(house_type, city, area, crawl_time):
    """
    获取数据库中抓取任务
    :return:
    """
    # 获取 mysql 连接
    coon = POOL.connection()
    cur = coon.cursor()
    sql = """insert into crawl_task(house_type, city, area, crawl_time) VALUES (%s, %s, %s, %s)"""
    try:
        cur.execute(sql, (house_type, city, area, crawl_time))
        coon.commit()
        result = True
    except Exception as e:
        logger.error(repr(e))
        coon.rollback()
        result = False
    finally:
        cur.close()
        coon.close()
    return result


def get_db_city():
    """
    获取数据库中城市中文名
    :return:
    """
    # 获取 mysql 连接
    coon = POOL.connection()
    cur = coon.cursor()
    sql_fang = """select a.area_code, a.area from area_city_ke a """

    sql_ershou = """select a.area_code, a.area from ershou_area_ke a """

    sql_city = """select a.city_code, a.city from provice_city_ke a """

    try:
        cur.execute(sql_fang)
        result_fang = cur.fetchall()
        cur.execute(sql_ershou)
        result_ershou = cur.fetchall()
        cur.execute(sql_city)
        result_city = cur.fetchall()

        result = {
            'result_fang': dict(result_fang),
            'result_ershou': dict(result_ershou),
            'result_city': dict(result_city)
        }

    except Exception as e:
        logger.error(repr(e))
        result = dict()
    finally:
        cur.close()
        coon.close()
    return result


def get_info(house_type, city, area):
    """
    获取数据库中抓取任务
    :return:
    """
    # 获取 mysql 连接
    coon = POOL.connection()
    cur = coon.cursor()
    sql_xiaoqu = """
    select a.id, b.city, ack.area, xiao.xiaoqu_name, xiao.houseinfo, xiao.positioninfo, xiao.taglist, xiao.price, xiao.on_sale
        from houses_city_ke a
        left join provice_city_ke b on a.city_code=b.city_code
        left join ershou_area_ke ack on a.area_code = ack.area_code
        join xiaoqu_info_ke xiao on xiao.houses_id = a.id
        where a.city_code=%s and a.area_code=%s
    """
    sql_ershou = """
    select a.id, b.city, ack.area, ershou.ershou_name, ershou.positioninfo, ershou.houseinfo, ershou.followinfo, ershou.tag, ershou.priceinfo
        from houses_city_ke a
        left join provice_city_ke b on a.city_code=b.city_code
        left join ershou_area_ke ack on a.area_code = ack.area_code
        join ershou_info_ke ershou on ershou.houses_id = a.id
        where a.city_code=%s and a.area_code=%s
    """
    sql_loupan = """
    select a.id, b.city, ack.area, houses.houses_title, houses.houses_type, houses.houses_status, houses.houses_location,
            houses.houses_room, houses.houses_tag, houses.houses_price
        from houses_city_ke a
        left join provice_city_ke b on a.city_code=b.city_code
        left join area_city_ke ack on a.area_code = ack.area_code
        join houses_info_ke houses on houses.houses_id = a.id
        where a.city_code=%s and a.area_code=%s
    """
    sql_dict = {
        'loupan': sql_loupan,
        'ershou': sql_ershou,
        'xiaoqu': sql_xiaoqu,
    }

    try:
        cur.execute(sql_dict[house_type], (city, area))
        result = cur.fetchall()
    except Exception as e:
        logger.error(repr(e))
        result = None
    finally:
        cur.close()
        coon.close()

    # 对楼盘的数据进行清理
    if house_type == 'loupan':
        """
        楼盘类型: 1住宅，2别墅，3商业，4写字楼，5底商
        楼盘状态: 1在售，2下期待开，3未开盘
        """
        loupan_type = {'1': '住宅', '2': '别墅', '3': '商业', '4': '写字楼', '5': '底商'}
        loupan_status = {'1': '在售', '2': '下期待开', '3': '未开盘'}
        result = [list(i) for i in result]
        for i in range(len(result)):
            for j in range(len(result[i])):
                if j == 4 and str(result[i][j]) in loupan_type:
                    result[i][j] = loupan_type[str(result[i][j])]
                elif j == 5 and str(result[i][j]) in loupan_type:
                    result[i][j] = loupan_status[str(result[i][j])]

    return result


def get_ch_city(city):
    # 获取 mysql 连接
    coon = POOL.connection()
    cur = coon.cursor()
    sql = """select city from provice_city_ke where city_code=%s"""
    try:
        cur.execute(sql, city)
        result = cur.fetchone()
    except Exception as e:
        logger.error(repr(e))
        result = None
    finally:
        cur.close()
        coon.close()
    return result


def get_ch_area(area, houses_type):
    # 获取 mysql 连接
    coon = POOL.connection()
    cur = coon.cursor()
    sql_fang = """select a.area from area_city_ke a where a.area_code=%s"""
    sql_ershou = """select a.area from ershou_area_ke a where a.area_code=%s"""
    sql_dict = {
        'loupan': sql_fang,
        'ershou': sql_ershou,
        'xiaoqu': sql_ershou,
    }
    try:
        cur.execute(sql_dict[houses_type], area)
        result = cur.fetchone()
    except Exception as e:
        logger.error(repr(e))
        result = None
    finally:
        cur.close()
        coon.close()
    return result


if __name__ == '__main__':
    print(get_ch_area('songjiang', 'ershou'))
