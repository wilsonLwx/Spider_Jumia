# __author__ = 'wilsonLwx'
# __date__ = '2019/3/2'
import difflib
import os
import csv

import re
from lxml import etree

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


def get_kw_url(kw):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "referer": "https://www.jumia.com.ng/computing/",
        "upgrade-insecure-requests": 1,
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
    }
    import urllib.request

    sub_url = 'https://www.jumia.com.ng/catalog/?q={}'.format(kw)
    rq = urllib.request.Request(sub_url, headers=headers)
    res = urllib.request.urlopen(rq)

    html = res.read().decode('utf-8')
    response = etree.HTML(html)
    page = response.xpath('/html/body/main/section/section[1]/div/div[2]/ul/li/a/@title')

    return res.url, page
