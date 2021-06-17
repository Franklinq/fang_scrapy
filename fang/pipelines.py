# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import copy

from scrapy.exporters import CsvItemExporter
from fang.items import NewHouseItem,EsfItem,ZufItem,MyCollectItem,UrlItem,ShopZuItem,ShopShouItem
from twisted.enterprise import  adbapi
from pymysql import cursors
import pymysql
class FangPipeline:
    def __init__(self):
        #url
        self.url_fp = open('url.csv', 'wb')
        self.url_exporter = CsvItemExporter(self.url_fp)
        #我的收藏
        self.mycollect_fp = open('mycollect.csv', 'wb')
        self.mycollect_exporter = CsvItemExporter(self.mycollect_fp)
        #新房
        self.newhouse_fp=open('newhouse.csv','wb')
        self.newhouse_exporter = CsvItemExporter(self.newhouse_fp)
        #二手房
        self.esfhouse_fp = open('esfhouse.csv', 'wb')
        self.esfhouse_exporter = CsvItemExporter(self.esfhouse_fp)
        #租房
        self.zuhouse_fp = open('zuhouse.csv', 'wb')
        self.zuhouse_exporter = CsvItemExporter(self.zuhouse_fp)
        #商铺出租
        self.shopzu_fp = open('shopzu.csv', 'wb')
        self.shopzu_exporter = CsvItemExporter(self.shopzu_fp)
        #商铺出售
        self.shopshou_fp = open('shopshou.csv', 'wb')
        self.shopshou_exporter = CsvItemExporter(self.shopshou_fp)

        db = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '159357',
            'database': 'fang',
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }

        self.dbpool = adbapi.ConnectionPool('pymysql', **db)
        self._sql = None

    #url
    def url_item(self, cursor, item):
        sql= """
                  insert into url(id,province,city,newhouse_url,esfhouse_url,zuhouse_url
                                  ,shop_zu_url,shop_shou_url)value(null,%s,%s,%s,%s,%s,%s,%s)
                  """
        cursor.execute(sql, (item['province'], item['city'], item['newhouse_url'], item['esfhouse_url'],
                             item['zuhouse_url'], item['shop_zu_url'], item['shop_shou_url']
                             ))
    #我的收藏
    def mycollect_item(self,cursor,item):
        sql="""
                      insert into mycollect(id,house_type,collect_time,title,url,room_type,area,orientation,floor,address,total,unit)
                                           value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                      """
        cursor.execute(sql, (item['house_type'], item['collect_time'], item['title'],item['url'], item['room_type'],
                                            item['area'],item['orientation'], item['floor'], item['address'],item['total'],
                                            item['unit']))
    #新房
    def newhouse_item(self,cursor,item):
        sql = """
                  insert into newhouse(id,province,city,village_name,newhousenews_url,room_type,area,region,address,
                                      state,price) value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
              """
        cursor.execute(sql, (item['province'], item['city'], item['village_name'],item['newhousenews_url'],
                                           item['room_type'],item['area'], item['region'], item['address'],item['state'],
                                           item['price']))
    #二手房
    def esfhouse_item(self,cursor,item):
        sql="""
                      insert into esfhouse(id,province,city,title,esfhousenews_url,room_type,area,floor,orientation,build_year,
                                          village_name,address,total,unit) value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                      """
        cursor.execute(sql, (item['province'], item['city'], item['title'],item['esfhousenews_url'], item['room_type'],
                                           item['area'],item['floor'], item['orientation'], item['build_year'],item['village_name'],
                                           item['address'],item['total'],item['unit']))
    #租房
    def zuhouse_item(self, cursor, item):
        sql="""
                      insert into zufhuose(id,province,city,title,housenews_url,zutype,room_type,area,orientation,address,
                                          money ) value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                      """
        cursor.execute(sql,(item['province'], item['city'], item['title'], item['housenews_url'], item['zutype'],
                           item['room_type'], item['area'], item['orientation'], item['address'], item['money']
                           ))
    #商铺出租
    def shopzu_item(self, cursor, item):
        sql="""
                   insert into shopzu(id,province,city,title,shopzunews_url,sign,address,shop_type,floor,area,money,
                                     day_money) value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
        cursor.execute(sql,(item['province'], item['city'], item['title'], item['shopzunews_url'], item['sign'],
                           item['address'], item['shop_type'], item['floor'], item['area'], item['money'],
                           item['day_money']))
    #商铺出售
    def shopshou_item(self, cursor, item):
        sql="""
                   insert into shopshou(id,province,city,title,shopshounews_url,sign,address,shop_type,floor,area,total,
                                       unit) value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
        cursor.execute(sql, (item['province'], item['city'], item['title'], item['shopshounews_url'],
                                           item['sign'], item['address'], item['shop_type'], item['floor'],
                                           item['area'],
                                           item['total'], item['unit']))

    def process_item(self, item, spider):
        #url
        if isinstance(item,UrlItem):
            # 保存到csv
            self.url_exporter.export_item(item)
            asynItem = copy.deepcopy(item)
            #其原因是由于Spider的速率比较快，而scapy操作数据库操作比较慢，
            # 导致pipeline中的方法调用较慢，这样当一个变量正在处理的时候，
            # 一个新的变量过来，之前的变量的值就会被覆盖，
            # 比如pipline的速率是1TPS，而spider的速率是5TPS，那么数据库应该会有5条重复数据。

            #保存到mysql
            defer = self.dbpool.runInteraction(self.url_item, asynItem)
            defer.addErrback(self.handle_error, asynItem)

        #我的收藏
        if isinstance(item,MyCollectItem):
            # 保存到csv
            self.mycollect_exporter.export_item(item)
            asynItem = copy.deepcopy(item)
            # 保存到mysql
            defer = self.dbpool.runInteraction(self.mycollect_item, asynItem)
            defer.addErrback(self.handle_error, asynItem)

        #新房
        if isinstance(item,NewHouseItem ):
            #保存到csv
            self.newhouse_exporter.export_item(item)
            asynItem = copy.deepcopy(item)
            #保存到mysql
            defer = self.dbpool.runInteraction(self.newhouse_item, asynItem)
            defer.addErrback(self.handle_error, asynItem)

         #二手房
        if isinstance(item,EsfItem):
            # 保存到csv
            self.esfhouse_exporter.export_item(item)
            asynItem = copy.deepcopy(item)
            # 保存到mysql
            defer = self.dbpool.runInteraction(self.esfhouse_item, asynItem)
            defer.addErrback(self.handle_error, asynItem)

        #租房
        if isinstance(item,ZufItem):
            # 保存到csv
            self.zuhouse_exporter.export_item(item)
            asynItem = copy.deepcopy(item)
            # 保存到mysql
            defer = self.dbpool.runInteraction(self.zuhouse_item, asynItem)
            defer.addErrback(self.handle_error, asynItem)

        #商铺出租
        if isinstance(item,ShopZuItem):
            # 保存到csv
            self.shopzu_exporter.export_item(item)
            asynItem = copy.deepcopy(item)
            # 保存到mysql
            defer = self.dbpool.runInteraction(self.shopzu_item, asynItem)
            defer.addErrback(self.handle_error, asynItem)

        #商铺出售
        if isinstance(item,ShopShouItem):
            # 保存到csv
            self.shopshou_exporter.export_item(item)
            asynItem = copy.deepcopy(item)
            # 保存到mysql
            defer = self.dbpool.runInteraction(self.shopshou_item, asynItem)
            defer.addErrback(self.handle_error, asynItem)

        return item


    def handle_error(self,error,item):
        print(error)

    def close_spider(self):
        self.url_fp.close()
        self.mycollect_fp.close()
        self.newhouse_fp.close()
        self.esfhouse_fp.close()
        self.zuhouse_fp.close()
        self.shopzu_fp.close()
        self.shopshou_fp.close()


