import csv
import json

import os
import requests
import latlng
import pandas as pd

shop_url = 'https://h5.ele.me/restapi/shopping/v3/restaurants'
food_url = 'https://h5.ele.me/restapi/shopping/v2/menu'
positions = [
    '39.932254,116.453598',
    '39.91229,116.45846',
    '39.90794,116.34517',
    '39.91899,116.35958',
    '39.89654,116.41936'
]
food_ids = []


def get_shops(params):
    response = requests.get(shop_url, params=params)
    restaurant__json = json.loads(response.text)
    shops = []
    restaurant__list = restaurant__json['items']
    for restaurant in restaurant__list:
        restaurant = restaurant['restaurant']
        shop = {
            'sid': restaurant['id'],
            'name': restaurant['name'],
            'orders': restaurant['recent_order_num']
        }
        shops.append(shop)
    return shops


def get_foods(sid):
    params = {'restaurant_id': sid}
    resopnse = requests.get(food_url, params=params)
    src_foods = json.loads(resopnse.text)
    dst_foods = []
    for src_food in src_foods:
        src_items = src_food['foods']
        for src_item in src_items:
            food_id = src_item['specfoods'][0]['food_id']
            original_price = src_item['specfoods'][0]['original_price']
            price = src_item['specfoods'][0]['price']
            if original_price is not None and price == 1:
                price = original_price
            if food_id in food_ids:
                continue
            food = {
                'name': src_item['specfoods'][0]['name'],
                'sale': src_item['specfoods'][0]['recent_popularity'],
                'price': price,
            }
            dst_foods.append(food)
            food_ids.append(food_id)
    return dst_foods


def obtain_csv(city, poses):
    for pos in poses:
        lat_lng = pos.split(',')
        params = {
            'latitude': lat_lng[0],
            'longitude': lat_lng[1],
            'offset': 0,
            'limit': 20,
            'terminal': 'h5',
            'order_by': 6
        }
        shop_list = get_shops(params)
        df = pd.DataFrame()
        for shop in shop_list:
            food_list = get_foods(shop['sid'])
            shop_foods = []
            for food in food_list:
                food_item = {
                    '城市': city,
                    '菜品': food['name'],
                    '月售': food['sale'],
                    '价格': food['price'],
                    '月销售额': food['sale'] * food['price'],
                    '店铺': shop['name'],
                    '店铺月售': shop['orders']
                }
                shop_foods.append(food_item)
    df = df.sort_values(by='月销售额')
    return df


if __name__ == '__main__':
    for city_file in os.listdir(latlng.ROOT_SS_PATH):
        city_file_path = os.path.join(latlng.ROOT_SS_PATH, city_file)
        df = pd.DataFrame(columns=['城市', '菜品', '月售', '价格', '月销售额', '店铺', '店铺月售'])
        for city_name, locations in city_file_path:
            for loc in locations:
                tmp_df = obtain_csv(city_name, loc)
                if df is None:
                    df = tmp_df
                else:
                    df.append(tmp_df)
