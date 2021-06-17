# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#url的Item
class UrlItem(scrapy.Item):
      # 省份
      province=scrapy.Field()
      # 城市
      city=scrapy.Field()
      #新房链接
      newhouse_url=scrapy.Field()
      # 二手房链接
      esfhouse_url=scrapy.Field()
      # 租房链接
      zuhouse_url=scrapy.Field()
      # 商铺出租链接
      shop_zu_url=scrapy.Field()
      # 商铺出售链接
      shop_shou_url=scrapy.Field()

#我的收藏页面的Item
class MyCollectItem(scrapy.Item):
      # 房子的类型
      house_type = scrapy.Field()
      # 收藏时间
      collect_time = scrapy.Field()
      # 房子的标题
      title = scrapy.Field()
      # 房子的详情链接
      url = scrapy.Field()
      # 户型
      room_type = scrapy.Field()
      # 面积
      area = scrapy.Field()
      # 朝向
      orientation = scrapy.Field()
      # 楼层
      floor = scrapy.Field()
      # 地址
      address = scrapy.Field()
      # 总价
      total = scrapy.Field()
      # 每平方米价格
      unit = scrapy.Field()

#新房页面的Item
class NewHouseItem(scrapy.Item):
      #省份
      province=scrapy.Field()
      #城市
      city = scrapy.Field()
      #小区的名字
      village_name = scrapy.Field()
      # 新房详细信息的链接
      newhousenews_url = scrapy.Field()
      #户型
      room_type = scrapy.Field()
      #面积
      area = scrapy.Field()
      #地区
      region = scrapy.Field()
      #地址
      address = scrapy.Field()
      #房子销售状态 在售、预售...
      state= scrapy.Field()
      #价格 一平米多少钱或一套多少钱
      price = scrapy.Field()

#二手房页面的Item
class EsfItem(scrapy.Item):
      # 省份
      province = scrapy.Field()
      # 城市
      city = scrapy.Field()
      #二手房的标题
      title = scrapy.Field()
      # 二手房详细信息的链接
      esfhousenews_url = scrapy.Field()
      # 户型
      room_type = scrapy.Field()
      # 面积
      area = scrapy.Field()
      # 楼层
      floor = scrapy.Field()
      # 朝向
      orientation = scrapy.Field()
      # 建筑时间
      build_year = scrapy.Field()
      # 小区名字
      village_name = scrapy.Field()
      # 地址
      address = scrapy.Field()
      # 总价
      total = scrapy.Field()
      #每平米的价格
      unit = scrapy.Field()

#租房页面的Item
class ZufItem(scrapy.Item):
      # 省份
      province = scrapy.Field()
      # 城市
      city = scrapy.Field()
      #房的标题
      title = scrapy.Field()
      # 房详细信息的链接
      housenews_url = scrapy.Field()
      # 租房类型
      zutype = scrapy.Field()
      # 户型
      room_type = scrapy.Field()
      # 面积
      area = scrapy.Field()

      # 朝向
      orientation = scrapy.Field()
      # 地址
      address = scrapy.Field()
      #月租
      money = scrapy.Field()

#商铺出租页面的Item
class ShopZuItem(scrapy.Item):
      # 省份
      province = scrapy.Field()
      # 城市
      city = scrapy.Field()
      #商铺的标题
      title = scrapy.Field()
      #商铺详细信息的链接
      shopzunews_url = scrapy.Field()
      #商铺所在标志
      sign = scrapy.Field()
      # 地址
      address = scrapy.Field()
      # 商铺出租类型
      shop_type = scrapy.Field()
      # 楼层
      floor = scrapy.Field()
      # 面积
      area = scrapy.Field()
      # 月租
      money = scrapy.Field()
      #每平米每天多少钱
      day_money = scrapy.Field()

#商铺出售页面的Item
class ShopShouItem(scrapy.Item):
      # 省份
      province = scrapy.Field()
      # 城市
      city = scrapy.Field()
      #商铺的标题
      title = scrapy.Field()
      #商铺详细信息的链接
      shopshounews_url = scrapy.Field()
      #商铺所在标志
      sign = scrapy.Field()
      # 地址
      address = scrapy.Field()
      # 商铺出租类型
      shop_type = scrapy.Field()
      # 楼层
      floor = scrapy.Field()
      # 面积
      area = scrapy.Field()
      # 总价
      total = scrapy.Field()
      # 每平米的价格
      unit = scrapy.Field()
