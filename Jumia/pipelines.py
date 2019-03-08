# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import pymongo

from utils.write_csv_func import write_csv


class JumiaPipeline(object):
    # 爬虫开启的方法
    def open_spider(self, spider):
        pass
        # 链接数据库
        # self.client = pymongo.MongoClient('127.0.0.1', 27017)
        # self.db = self.client['Jumia']
        # self.collection = self.db['room']

    def process_item(self, item, spider):
        dict_data = dict(item)
        # 写入文件名称 名字可自行更改
        file_name = './test2.csv'
        write_csv(dict_data, file_name)
        # self.collection.insert(dict_data)
        # return item

    def close_spider(self, spider):
        pass
        # self.client.close()
        # self.f.close()
