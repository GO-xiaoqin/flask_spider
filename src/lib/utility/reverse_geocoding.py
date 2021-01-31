# -*- coding: utf-8 -*-
import json
import requests
from urllib.parse import quote
from conf import AK


def getlnglat(address, city):
    """
    逆地理编码
    :param address: 查询地址拼接 城市，县区小区名字
    :param city: 指定查询城市范围
    :return:
    """
    url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}&city={}'
    ak = AK
    address = quote(address) # 由于本文地址变量为中文，为防止乱码，先用quote进行编码
    city = quote(city)
    uri = url.format(address, ak, city)
    req = requests.get(uri)
    try:
        temp = json.loads(req.text)
    except Exception:
        lat = 0
        lng = 0
    else:
        if temp['status'] == 0:
            lat = temp['result']['location']['lat']
            lng = temp['result']['location']['lng']
        else:
            lat = 0
            lng = 0
    return lat, lng


if __name__ == '__main__':
    """http://api.map.baidu.com/geocoding/v3/?address=北京市海淀区上地十街10号&output=json&ak=您的ak&callback=showLocation"""
    address = '上海松江新凯一期'
    city = '上海'
    print(getlnglat(address, city))
