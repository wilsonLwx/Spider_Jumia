# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JumiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 所需采集字段
    Name = scrapy.Field()

    PrimaryCategory = scrapy.Field()

    Brand = scrapy.Field()

    Model = scrapy.Field()

    Color = scrapy.Field()

    SalePrice = scrapy.Field()

    Price = scrapy.Field()

    ProductLine = scrapy.Field()

    ColorFamily = scrapy.Field()

    Description = scrapy.Field()

    ShortDescription = scrapy.Field()

    PackageContent = scrapy.Field()
    ProductMeasures = scrapy.Field()
    ProductWeight = scrapy.Field()
    ProductWarranty = scrapy.Field()
    SellerSku = scrapy.Field()
    ParentSku = scrapy.Field()
    Variation = scrapy.Field()
    Quantity = scrapy.Field()
    MainImage = scrapy.Field()
    Keywrds = scrapy.Field()
    SaleStartDate = scrapy.Field()
    SaleEndDate = scrapy.Field()
    MainMaterial = scrapy.Field()
    ProductId = scrapy.Field()
