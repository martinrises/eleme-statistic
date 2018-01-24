import os
import requests
import json
from pypinyin import lazy_pinyin

delt = 0.05
step = 3


ROOT_PATH = '/home/liuzhf/workspace/projects/elema-statistic'
ROOT_SS_PATH = os.path.join(ROOT_PATH, 'shanshan_list/')


def calculate_points(city, center_lat, center_lng):
    start_lat = center_lat + delt * step
    start_lng = center_lng - delt * step
    latng_list = []
    for index_lat in range(1, step * 2 + 1):
        for index_lng in range(1, step * 2 + 1):
            lat_lng = '{},{}'.format(start_lat - index_lat * delt, start_lng + index_lng * delt)
            latng_list.append(lat_lng)
    return {city: latng_list}


def get_city_locations(city_file_path):
    response = requests.get('https://mainsite-restapi.ele.me/shopping/v1/cities')
    json_dict = json.loads(response.text)
    city_dict={}
    for _,citys in json_dict.items():
        for city in citys:
            city_dict[city['pinyin']] = '{},{}'.format(city['latitude'], city['longitude'])

    city_loctions_dict = {}
    with open(city_file_path, 'r') as f:
        for l in f.readlines():
            city_name = l.split()[0]
            # shanshan pinyin list
            city_name_pinyin = ''.join(lazy_pinyin(city_name))
            try:
                city_loctions_dict[city_name] = city_dict[city_name_pinyin]
            except:
                print('{} not found >>> {}'.format(city_name, city_name_pinyin))
    return city_loctions_dict

