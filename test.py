# -*- coding: utf-8 -*- 
# date: 21-1-8 下午4:34
from src.lib.utility.db_pool import get_area_city
from pprint import pprint

if __name__ == '__main__':
    result = get_area_city()

    result_city = {i[3]: i[2] for i in result['result_fang']}
    result_city = [{'city_name': result_city[i], 'city_code': i, 'area': []} for i in result_city]
    result_ = [{'name': i, 'city': []} for i in set([i[4] for i in result['result_fang']])]

    for i in result['result_fang']:
        for j in range(len(result_city)):
            if i[3] in result_city[j]['city_code']:
                result_city[j]['area'].append({'area_name': i[0], 'area_code': i[1]})
                result_city[j]['provice'] = i[4]
    for i in result_city:
        for j in range(len(result_)):
            if i['provice'] == result_[j]['name']:
                result_[j]['city'].append(i)

    pprint(result_)

