# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import pymongo

from utils.write_csv_func import write_csv


class JumiaPipeline(object):
    total_count = 0
    success_count = 0
    fail_count = 0

    # 爬虫开启的方法
    def open_spider(self, spider):
        # 链接数据库
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client['Jumia']
        self.collection = self.db['room']

    def process_item(self, item, spider):
        self.total_count += 1
        dict_data = dict(item)
        # 写入文件名称 名字可自行更改
        file_name = './test2.csv'
        write_csv(dict_data, file_name)
        self.collection.insert(dict_data)
        # return item
        if dict_data:
            self.success_count += 1
            return '第{}条数据,采集{},当前成功{}条，失败{}条'.format(self.total_count, 'success', self.success_count, self.fail_count)
        else:
            self.fail_count += 1
            return '第{}条数据,采集{},当前成功{}条，失败{}条'.format(self.total_count, '失败', self.success_count, self.fail_count)

    def close_spider(self, spider):
        print("总共采集{}条，成功{}条，失败{}条".format(self.total_count, self.success_count, self.fail_count))
        self.client.close()
        # self.f.close()
