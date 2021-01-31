# -*- coding: utf-8 -*- 
# date: 21-1-12 上午9:44
# 统一配置文件
# 对接百度地图API逆地理编码
AK = '3b64bZEZUh4AGwNIoxNc8BPuctfXXtWO'

# redis
REDIS_IP = '119.8.116.167'
REDIS_USER = ''
REDIS_PWD = 'Xu551212'
REDIS_URL = "redis://{}:{}@{}/0".format(REDIS_USER, REDIS_PWD, REDIS_IP)

# mysql
MYSQL_HOST = '119.8.116.167'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PWD = 'Xu551212'
MYSQL_DB = 'test'

# app.py 启动配置
HOST = '0.0.0.0'
PORT = 8883
DEBUG = False
