# -*- coding: utf-8 -*- 
# date: 21-1-12 上午9:44
# 统一配置文件
# 对接百度地图API逆地理编码
AK = '***'

# redis
REDIS_IP = '***'
REDIS_USER = ''
REDIS_PWD = '***'
REDIS_URL = "redis://{}:{}@{}/0".format(REDIS_USER, REDIS_PWD, REDIS_IP)

# mysql
MYSQL_HOST = '***'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PWD = '***'
MYSQL_DB = 'test'

# app.py 启动配置
HOST = '0.0.0.0'
PORT = 8883
DEBUG = False
