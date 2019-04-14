# -*- coding: utf-8 -*-
import re
import os
import scrapy


from Jumia.items import JumiaItem
from utils.get_conf_data import get_category_id, gen_data
from utils.write_csv_func import read_csv

BASE_DIR = os.path.dirname(os.path.realpath('__file__'))


class JumiaSpider(scrapy.Spider):
    print(BASE_DIR)
    name = 'jumia'
    allowed_domains = ['jumia.com.ng']
    # 此处更换 爬取url
    base_url = 'https://www.jumia.com.ng/category-fashion-by-jumia/'
    start_urls = [base_url]
    temp_list = []
    # def parse(self, response):
    #     sub_urls = []
    #     category_list = response.xpath('//*[@id="menuFixed"]/ul/li/a/@href').extract()
    #     for category in category_list:
    #         if 'computing' in category:
    #             sub_urls.append(category)
    #         elif 'electronics' in category:
    #             sub_urls.append(category)
    #         elif 'video-games' in category:
    #             sub_urls.append(category)
    #     for sub_url in sub_urls:
    #         yield scrapy.Request(url=sub_url, meta={'sub_url': sub_url}, callback=self.second_parse)
    #
    # def second_parse(self, response):
    #     # 如果需要关键字爬取 请打开此段代码 注释掉下两段代码
    #     sub_url, page = get_kw_url('computer')
    #
    #     # 如果想整页爬取 请注释掉关键字查询代码 打开下两段代码
    #     # 获取第一页的数据
    #     # page = response.xpath('/html/body/main/section/section[1]/div/div[2]/ul/li/a/@title').extract()
    #     # 获取商品页的url
    #     # sub_url = response.meta.get('sub_url')
    #
    #     # 取最大页数
    #     page_count = int(page[-2])
    #     # 循环累计添加页数
    #     for i in range(1, page_count + 1):
    #         re_url = re.findall(r'(https://www.jumia.com.ng/.*/)?.*', sub_url)
    #         # 如果有值 取值
    #         if re_url:
    #             sub_url = re_url[0]
    #         sub_url = sub_url + '?page={}'.format(i)
    #         yield scrapy.Request(url=sub_url, callback=self.detail_parse)

    page = 0

    def parse(self, response):

        str_ = response.url
        total_page = int(response.xpath('/html/body/main/section/section[1]/div/div[2]/ul/li/a/@title').extract()[-2])
        for page in range(1, total_page + 1):
            self.page += 1
            index = str_.find('&page=')
            if index != -1:
                rq_url = str_[:index]
                rq_url = rq_url + '&page={}'.format(self.page)

            else:
                res = re.match(r'http.*?\?\w+=\w+', str_)
                if res:
                    rq_url = str_ + '&page={}'.format(self.page)
                else:
                    rq_url = str_ + '?page={}'.format(self.page)

            yield scrapy.Request(url=rq_url, callback=self.detail_parse)

    def detail_parse(self, response):

        # 商品列表页url 爬取
        detail_urls = response.xpath('/html/body/main/section/section[2]/div/a/@href').extract()

        # 自定义单个商品爬取 需开启下面代码其中之一 上面代码需要注释掉 如数量不多 直接在下面定义['url1','url2']
        # detail_urls = ['url1', 'url2']

        # 如数量多也可通过配置 文件yaml配置 使用下面方法读取文件
        # detail_url = gen_data()
        for detail_url in detail_urls:
            yield scrapy.Request(url=detail_url, callback=self.finaly_parse)

    def finaly_parse(self, response):
        base_url = response.url
        seller_sku = re.match(r'.*?(\d+)\.html', base_url).group(1)
        # 对于seller_sku重复的 去重
        if seller_sku not in self.temp_list:
            self.temp_list.append(seller_sku)
        else:
            return
        # 下面为三种卖家的情况 需要哪个就开启那段代码 其余注释掉

        # 海外仓
        # no_label = response.xpath('/html/body/main/section[1]/div[2]/div[1]/div[6]/div[1]/span/span/@class')
        # if no_label == 'osh-icon -jumia-express shop_express--logo':

        # 全球卖家
        no_label = response.xpath('/html/body/main/section[1]/div[2]/div[2]/div/div[1]/text()').extract()
        if '  Shipped from overseas ' in no_label:

            # local 卖家
            # express_label = response.xpath('/html/body/main/section[1]/div[2]/div[1]/div[6]/div[1]/span/span/@class')
            # global_label = response.xpath(
            #     '/html/body/main/section[1]/div[2]/div[2]/div/div[1]/text()').extract()  # 解析数据 将数据存入管道 xpath做了封装 返回list
            # if not (express_label and global_label):

            data_list = response.xpath('/html/body/main')
            data_element = data_list[0]
            item_dict = JumiaItem()
            item_dict['SellerSku'] = seller_sku
            item_dict['ParentSku'] = item_dict['SellerSku']
            str_ = data_element.xpath('./section[1]/div[2]/div[1]/span/h1/text()')[0].extract()
            item_dict['Name'] = re.match(r'.*? (.*)', str_).group(1)
            item_dict['Keywrds'] = item_dict['Name']
            item_dict['Brand'] = data_element.xpath('./section[1]/div[2]/div[1]/div[1]/a/text()').extract_first()
            pd = data_element.xpath('//*[@id="product-details"]').extract_first()
            product_details = pd if pd is not None else ''
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

            if product_el1:
                item_dict['ProductLine'] = product_el1[0]
            elif product_el2:
                item_dict['ProductLine'] = product_el2[0]
            else:
                item_dict['ProductLine'] = ''

            cat_str_list = data_element.xpath('./nav/ul/li/a/text()').extract()
            # 调用读取对比文件category_tree_export.csv的方法
            new_list = read_csv(BASE_DIR + '/conf/category_tree_export.csv')
            new_str = ''.join(cat_str_list)
            # 调用过去PrimaryCategory的方法
            sku_id = get_category_id(new_str, new_list)
            item_dict['PrimaryCategory'] = sku_id

            item_dict['SalePrice'] = data_element.xpath(
                '//*[@class="price-box"]/div[1]/span/span[2]/text()').extract_first()
            price = data_element.xpath('//*[@class="price-box"]/span/span[2]/text()').extract_first()
            item_dict['Price'] = price if price else item_dict['SalePrice']
            image_list = data_element.xpath('//*[@class="media"]/div[1]/div/a/@href').extract()

            item_dict['MainImage'] = image_list[0] if len(image_list) >= 1 else ''
            item_dict['Image2'] = image_list[1] if len(image_list) >= 2 else ''
            item_dict['Image3'] = image_list[2] if len(image_list) >= 3 else ''
            item_dict['Image4'] = image_list[3] if len(image_list) >= 4 else ''
            item_dict['Image5'] = image_list[4] if len(image_list) >= 5 else ''
            item_dict['Image6'] = image_list[5] if len(image_list) >= 6 else ''
            item_dict['Image7'] = image_list[6] if len(image_list) >= 7 else ''
            item_dict['Image8'] = image_list[7] if len(image_list) >= 8 else ''

            item_dict['Description'] = ''.join(data_element.xpath('//*[@id="productDescriptionTab"]/node()').extract())
            item_dict['ShortDescription'] = ''.join(
                data_element.xpath('//*[@id="product-details"]/div[1]/node()').extract())
            item_dict['ColorFamily'] = 'Multi'
            item_dict['PackageContent'] = ''.join(
                data_element.xpath('//*[@id="product-details"]/div[2]/node()').extract())

            # 获取variation字段所有内容
            variation = data_element.xpath(
                '/html/body/main/section[1]/div[2]/div[1]/div[6]/div/div[1]/span/node()').extract()
            # 对内容进行筛选
            if variation:
                if len(variation) >= 2:
                    if variation[0] != '...':
                        item_dict['Variation'] = variation[0]
                    else:
                        item_dict['Variation'] = variation[1]
                else:
                    item_dict['Variation'] = variation[0]
            # 如果该字段没有内容 设置为空串
            else:
                item_dict['Variation'] = ''

            item_dict['Quantity'] = 50
            item_dict['SaleStartDate'] = '2019-01-28'
            item_dict['SaleEndDate'] = '2030-01-28'
            item_dict['ProductId'] = ''
            item_dict['Model'] = ''
            item_dict['ProductWarranty'] = 'N/A'
            # 加入任务名称
            item_dict['TaskName'] = ''

            yield item_dict
        else:
            pass
