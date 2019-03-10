# -*- coding: utf-8 -*-
import difflib
import re

import os
import scrapy

from Jumia.items import JumiaItem
from utils.get_conf_data import get_category_id
from utils.write_csv_func import read_csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class JumiaSpider(scrapy.Spider):
    name = 'jumia'
    allowed_domains = ['jumia.com.ng']
    # base_url = 'https://www.jumia.com.ng/'
    # format()括号里输入关键字极客爬取
    base_url = 'https://www.jumia.com.ng/catalog/?q={}'.format('computer')
    start_urls = [base_url]
    page = 1

    def parse(self, response):
        sub_urls = []
        category_list = response.xpath('//*[@id="menuFixed"]/ul/li/a/@href').extract()
        for category in category_list:
            if 'computing' in category:
                sub_urls.append(category)
            elif 'electronics' in category:
                sub_urls.append(category)
            elif 'video-games' in category:
                sub_urls.append(category)
        for sub_url in sub_urls:
            yield scrapy.Request(url=sub_url, meta={'sub_url': sub_url}, callback=self.second_parse)

    def second_parse(self, response):
        # 获取第一页的数据
        page = response.xpath('/html/body/main/section/section[1]/div/div[2]/ul/li/a/@title').extract()
        page_count = int(page[-2])
        sub_url = response.meta.get('sub_url')
        # 循环累计添加页数
        for i in range(1, page_count + 1):
            re_url = re.match(r'(https://www.jumia.com.ng/.*/)?.*', sub_url)
            # 如果有值 取值
            if re_url is not None:
                sub_url = re_url.group(1)
            sub_url = sub_url + '?page={}'.format(i)
            yield scrapy.Request(url=sub_url, callback=self.detail_parse)

    def detail_parse(self, response):

        # 商品类表页url
        detail_urls = response.xpath('/html/body/main/section/section[2]/div/a/@href').extract()
        for detail_url in detail_urls:
            yield scrapy.Request(url=detail_url, callback=self.finaly_parse)

    def finaly_parse(self, response):
        base_url = response.url
        # 不采集标签
        no_label = response.xpath('/html/body/main/section[1]/div[2]/div[1]/div[6]/div[1]/span/span/@class')

        # 如果不是以上标签，就执行采集任务
        if no_label != 'osh-icon -jumia-express shop_express--logo':
            # 解析数据 将数据存入管道 xpath做了封装 返回list
            data_list = response.xpath('/html/body/main')
            data_element = data_list[0]
            item_dict = JumiaItem()
            item_dict['SellerSku'] = re.match(r'.*?(\d+)\.html', base_url).group(1)
            item_dict['ParentSku'] = item_dict['SellerSku']
            str_ = data_element.xpath('./section[1]/div[2]/div[1]/span/h1/text()')[0].extract()
            item_dict['Name'] = re.match(r'.*? (.*)', str_).group(1)
            item_dict['Keywrds'] = item_dict['Name']
            item_dict['Brand'] = data_element.xpath('./section[1]/div[2]/div[1]/div[1]/a/text()').extract_first()
            product_details = data_element.xpath('//*[@id="product-details"]').extract_first()
            product_description_tab = data_element.xpath('//*[@id="productDescriptionTab"]').extract_first()
            # 查找产品详情或者描述下那个包含Color
            color_el1 = re.findall(r'Colour</div>.*?>(.*?)</div>?', product_details, re.S)
            color_el2 = re.findall(r'Colour</div>.*?>(.*?)</div>?', product_description_tab, re.S)

            if color_el1:
                item_dict['Color'] = color_el1[0]
            elif color_el2:
                item_dict['Color'] = color_el2[0]
            else:
                item_dict['Color'] = ''

            # 查找产品详情或者描述下那个包含Weight
            weight_el1 = \
                re.findall(r'Weight.*>(\d+.\d+)<', product_details, re.S)
            weight_el2 = \
                re.findall(r'Weight.*>(\d+.\d+)<', product_description_tab, re.S)
            if weight_el1:
                item_dict['ProductWeight'] = weight_el1[0]
            elif weight_el2:
                item_dict['ProductWeight'] = weight_el2[0]
            else:
                item_dict['ProductWeight'] = ''

            # 查找产品详情或者描述下那个包含MainMaterial
            material_el1 = re.findall(r'Main material</div>.*?>(.*?)</div>?', product_details, re.S)
            material_el2 = re.findall(r'Main material</div>.*?>(.*?)</div>?', product_description_tab, re.S)
            if material_el1:
                item_dict['MainMaterial'] = material_el1[0]
            elif material_el2:
                item_dict['MainMaterial'] = material_el2[0]
            else:
                item_dict['MainMaterial'] = ''

            # 查找产品详情页尺寸
            size_el1 = re.findall(r'\d+[\.]*\d*\*\d+[\.]*\d*\*\d+[\.]*\d*\w*', product_details, re.S)
            size_el2 = re.findall(r'\d+[\.]*\d*\*\d+[\.]*\d*\*\d+[\.]*\d*\w*', product_description_tab, re.S)

            if size_el1:
                item_dict['ProductMeasures'] = size_el1[0]
            elif size_el2:
                item_dict['ProductMeasures'] = size_el2[0]
            else:
                item_dict['ProductMeasures'] = ''

            product_el1 = re.findall(r'Product Line</div>.*?>(.*?)</div>?', product_details, re.S)
            product_el2 = re.findall(r'Product Line</div>.*?>(.*?)</div>?', product_description_tab, re.S)

            if size_el1:
                item_dict['ProductLine'] = product_el1[0]
            elif size_el2:
                item_dict['ProductLine'] = product_el2[0]
            else:
                item_dict['ProductLine'] = ''

            cat_str_list = data_element.xpath('./nav/ul/li/a/text()').extract()
            # 调用读取对比文件category_tree_export.csv的方法
            new_list = read_csv(os.path.join(BASE_DIR, 'conf/category_tree_export.csv'))
            new_str = ''.join(cat_str_list)
            # 调用过去PrimaryCategory的方法
            sku_id = get_category_id(new_str, new_list)
            item_dict['PrimaryCategory'] = sku_id

            item_dict['SalePrice'] = ' '.join(data_element.xpath(
                '//*[@class="price-box"]/div[1]/span/span/text()').extract())
            item_dict['Price'] = ' '.join(data_element.xpath('//*[@class="price-box"]/span/span/text()').extract())
            item_dict['MainImage'] = ','.join(data_element.xpath('//*[@class="media"]/div[1]/div/a/@href').extract())
            item_dict['Description'] = ''.join(data_element.xpath('//*[@id="productDescriptionTab"]/node()').extract())
            item_dict['ShortDescription'] = ''.join(
                data_element.xpath('//*[@id="product-details"]/div[1]/node()').extract())
            item_dict['ColorFamily'] = 'Multi'
            item_dict['PackageContent'] = ''.join(
                data_element.xpath('//*[@id="product-details"]/div[2]/node()').extract())

            variation = data_element.xpath('./section[1]/div[2]/div[1]/div[7]/div[1]/div[1]/span/node').extract()
            if variation:
                item_dict['Variation'] = ''.join(variation)
            else:
                item_dict['Variation'] = ''

            item_dict['Quantity'] = 50
            item_dict['SaleStartDate'] = '209-01-28'
            item_dict['SaleEndDate'] = '2030-01-28'
            item_dict['ProductId'] = ''
            item_dict['Model'] = ''
            item_dict['ProductWarranty'] = 'N/A'

            yield item_dict
        else:
            pass
