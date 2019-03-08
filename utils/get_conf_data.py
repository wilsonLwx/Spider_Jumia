# __author__ = 'wilsonLwx'
# __date__ = '2019/3/2'
import difflib
import os
import csv

import re
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def get_conf():
    with open(BASE_DIR + '/conf/conf.yaml', 'r') as f:
        content = yaml.load(f)
        return content


def gen_data():
    content = get_conf()
    base_urls = content.get('base_url')
    return base_urls


def get_category_id(new_str, new_list):
    temp_dict = {}
    for index in range(len(new_list)):
        # 1. difflib
        # 对比字符串相似度 ，根据相似度赋值categoryId
        seq = difflib.SequenceMatcher(None, new_str, new_list[index])
        ratio = seq.ratio()
        temp_dict.update({new_list[index]: ratio})
    max_ratio = max(temp_dict.values())
    sku_id = ''
    for k, v in temp_dict.items():
        if v == max_ratio:
            # 截取ID
            sku_id = re.match(r'\d+', k).group()
    # 返回
    return sku_id
