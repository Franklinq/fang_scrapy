# -*- coding: utf-8 -*-
import scrapy
import re
import time
from selenium import webdriver
from fang.items import NewHouseItem,EsfItem,ZufItem,ShopZuItem,ShopShouItem,MyCollectItem,UrlItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class TxSpider(scrapy.Spider):
    name = 'tx'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']
    login_url='https://passport.fang.com/'
    mycollect_url='https://my.fang.com/MyCollect/Index.html'
    # redis_key = "tx:start_url"

    cookies_dict={}

     #模拟登录
    def parse(self,response):
        driver = webdriver.Chrome()
        driver.get(self.login_url)
        time.sleep(2)

        js_phone = "document.getElementsByTagName('dd')[0].style.display='none'"
        js_account= "document.getElementsByTagName('dd')[1].style.display='block'"
        driver.execute_script(js_phone)
        driver.execute_script(js_account)

        driver.find_element_by_id("username").click()
        username=driver.find_element_by_xpath("//input[@id='username']").send_keys('eqws')
        driver.find_element_by_id("password").click()
        password = driver.find_element_by_xpath("//input[@id='password']").send_keys('123456zx')

        submit=driver.find_element_by_xpath("//button[@id='loginWithPswd']")
        submit.click()
        print('登录成功')
        time.sleep(3)

        cookies=driver.get_cookies()
        for cookie in cookies:
            # 在保存成dict时，我们其实只要cookies中的name和value，而domain等其他都可以不要
            self.cookies_dict[cookie['name']] = cookie['value']
        driver.quit()
        yield scrapy.Request(url='https://www.fang.com/SoufunFamily.htm',cookies=self.cookies_dict,callback=self.parse_url)
        # 请求我的收藏页面
        yield scrapy.Request(url=self.mycollect_url, cookies=self.cookies_dict, callback=self.parse_mycollect,
                             errback=self.errback_httpbin)

    #获取爬取的链接
    def parse_url(self,response):

        item = UrlItem()
        #获取数据的每一行tr
        trs=response.xpath("//div[@class='outCont']//tr")
        for tr in trs:
            #获取省份的td
            tds=tr.xpath(".//td[not(@class)]")
            province_td=tds[0]
            # #获取省份的值
            province_text=province_td.xpath(".//text()").get()
            # #给省份去掉 多余空格
            province_text=re.sub( r'\s','',province_text)
            #判断省份是否为空的
            if province_text:
                #将不为空的省份赋值给province
                province=province_text
                #除去国外的链接
                if province=='其它':
                    break
                if province=='重庆' or province=='天津' :
                    continue
                item['province']=province

            #获取城市的td
            city_td = tds[1]
            #获取到城市的a
            city_links=city_td.xpath(".//a")

            for city_link in city_links:
                #城市
                city=city_link.xpath(".//text()").get()
                item['city'] = city
                #城市的链接
                city_url=city_link.xpath(".//@href").get()
                #以点分割城市的链接
                city_url_list=city_url.split('.')
                # print(city_url_list)
                #拼接城市新房链接
                newhouse_url=city_url_list[0]+'.newhouse.'+city_url_list[1]+'.'+city_url_list[2]
                item['newhouse_url'] = newhouse_url
                #拼接城市二手房链接
                esfhouse_url=city_url_list[0]+'.esf.'+city_url_list[1]+'.'+city_url_list[2]
                item['esfhouse_url'] = esfhouse_url

                #拼接城市租房链接,北京为特例
                if city_url_list[0]=='http://bj':
                    zuhouse_url='https://zu.fang.com/'
                    item['zuhouse_url'] = zuhouse_url
                else:
                    zuhouse_url=city_url_list[0]+'.zu.'+city_url_list[1]+'.'+city_url_list[2]
                    item['zuhouse_url'] = zuhouse_url
                #商铺出租
                if city_url_list[0] == 'http://bj':
                    shop_zu_url = 'https://shop.fang.com/zu/house/'
                    item['shop_zu_url'] = shop_zu_url
                else:
                    shop_zu_url = city_url_list[0] + '.shop.' + city_url_list[1] + '.' + city_url_list[2] + 'zu/house/'
                    item['shop_zu_url'] = shop_zu_url
                # 商铺出售
                if city_url_list[0] == 'http://bj':
                    shop_shou_url = 'https://shop.fang.com/shou/house/'
                    item['shop_shou_url'] = shop_shou_url
                else:
                    shop_shou_url = city_url_list[0] + '.shop.' + city_url_list[1] + '.' + city_url_list[2] + 'shou/house/'
                    item['shop_shou_url'] = shop_shou_url


                yield  item
                #请求新房页面
                yield scrapy.Request(url=newhouse_url, cookies=self.cookies_dict, callback=self.parse_newhouse,
                                     meta={"info": (province, city)})
                #请求二手房页面
                yield scrapy.Request(url=esfhouse_url, cookies=self.cookies_dict, callback=self.parse_esfhouse,
                                     meta={"info": (province, city)})
                #请求租房页面
                yield scrapy.Request(url=zuhouse_url, cookies=self.cookies_dict, callback=self.parse_zuhouse,
                                    meta={"info": (province, city)})
                #请求商铺出租页面
                yield scrapy.Request(url=shop_zu_url, cookies=self.cookies_dict, callback=self.parse_shop_zu,
                                    errback=self.errback_httpbin, meta={"info": (province, city)})
                #请求商铺出售页面
                yield scrapy.Request(url=shop_shou_url, cookies=self.cookies_dict, callback=self.parse_shop_shou,
                                     errback=self.errback_httpbin, meta={"info": (province, city)})


    #我的收藏页面
    def parse_mycollect(self, response):
        item = MyCollectItem()
        print("-------------------------------------------------对于我的收藏页面的解析--------------------------------------------------")
        ul=response.xpath("//ul[@class='collect_list']/li")
        if ul:
            for li in ul:
                #房子的类型 如二手房、新房...
                house_type=''.join(li.xpath(".//div[@class='collect_tit']/text()").getall()).strip()
                item['house_type']=house_type

                #收藏时间
                collect_time=li.xpath(".//div[@class='collect_tit']/i/text()").get()
                item['collect_time'] = collect_time

                #房子的标题
                title=li.xpath(".//div[@class='collect_info']/b/a/text()").get()
                item['title'] = title

                #房子的详情链接
                url=li.xpath(".//div[@class='collect_info']/b/a/@href").get()
                if 'http:' not in url:
                    url=response.urljoin(url)
                item['url'] = url

                #房子的信息
                lists="".join(li.xpath(".//div[@class='collect_info']/p[1]/text()").getall()).split()
                item['room_type'] = ''
                item['area'] = ''
                item['orientation'] = ''
                item['floor'] = ''
                for list in lists:
                    if '厅' in list:
                        # 户型
                        room_type=list
                        item['room_type'] = room_type
                    elif '㎡' in list:
                        #面积
                        area=list
                        item['area'] = area
                    elif '向' in list:
                        #朝向
                        orientation=list
                        item['orientation'] = orientation
                    elif '层' in list:
                        #楼层
                        floor = list
                        item['floor'] = floor

                #地址
                address="".join(li.xpath(".//div[@class='collect_info']/p[2]/text()").getall()).replace(u'\xa0', u'/')
                item['address'] = address
                # 每平方米价格
                unit = li.xpath(".//div[@class='collect_right']/p/text()").get()
                item['unit'] = unit
                #总价
                total=li.xpath(".//div[@class='collect_right']/b/text()").get()
                if '/' in total:
                    unit=total
                    item['unit'] = unit
                    item['total'] = ''
                item['total'] = total

                yield  item


    #对于新房页面的解析
    def parse_newhouse(self,response):
        print("-------------------------------------------------对于新房页面的解析--------------------------------------------------")
        province,city=response.meta.get("info")
        lis=response.xpath("//div[contains(@class,'nl_con')]//li[contains(@id,'lp')]")
        for li in lis:

            name_text=li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            village_name=''
            if name_text:
                #小区名字
                village_name=name_text.strip()


            newhousenews_url = ''
            href=li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            if href:
                #新房详细链接
                newhousenews_url="https:"+li.xpath(".//div[@class='nlcd_name']/a/@href").get()

            #获取户型
            type_text=li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()
            #过滤户型
            room_type=list(filter(lambda x:x.endswith(("居","上")),type_text))
            #转换成以/作为分割的字符串
            room_type="/".join(room_type)

            #获取面积
            area=''
            area_list = "".join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall()).split()
            if area_list:
                area=area_list[-1]
            else:
                area=''
            #获取地区
            region = ''
            span=li.xpath(".//div[@class='address']/a/span").get()

            #有的页面有a标签下span，有的没有 所以判断一下
            if span:
                # 地区
                region_text=li.xpath(".//div[@class='address']/a/span/text()").get().strip()
                region = re.sub(r'\[|\]', '', region_text)
                # 地址
                address=li.xpath(".//div[@class='address']/a/@title").get()
            else:
                list_text=' '.join(li.xpath(".//div[@class='address']/a/text()").getall()).split()
                address=''
                if list_text:
                   if len(list_text)==1:
                        # 地址
                       address=list_text[0]
                   else:
                        #地区
                       region=re.sub(r'\[|\]','',list_text[0])
                       address = list_text[1]

            #房子销售状态
            state=li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()

            #价格
            price=''
            price_list="".join(li.xpath(".//div[@class='nhouse_price']//text()").getall()).split()
            if price_list:
               price=price_list[-1]
            item=NewHouseItem(province=province,city=city,village_name=village_name,newhousenews_url=newhousenews_url,
                              room_type=room_type,area=area,address=address,region=region,state=state,price=price)
            yield item


        #下一页的链接
        next_link=response.urljoin(response.xpath("//li[@class='fr']/a[@class='next']/@href").get())
        # 如果不为转跳到下一页
        if next_link:
            yield  scrapy.Request(url=next_link,callback=self.parse_newhouse,meta={"info":(province,city)})


    # 对于二手房页面的解析
    def parse_esfhouse(self,response):
        print("-------------------------------------------------对于二手房页面的解析--------------------------------------------------")
        item = EsfItem()
        province, city = response.meta.get("info")
        item['province'] = province
        item['city'] = city
        dls=response.xpath("//dl[@dataflag='bg']")
        for dl in dls:
            item['build_year'] = ''
            #二手房标题
            title=dl.xpath(".//h4[@class='clearfix']/a/@title").get()
            item['title'] = title
            #二手房详情链接
            esfhousenews_url_text=dl.xpath(".//h4[@class='clearfix']/a/@href").get()
            esfhousenews_url=response.urljoin(esfhousenews_url_text)
            # print(esfhousenews_url)
            item['esfhousenews_url'] = esfhousenews_url
            #二手房信息
            lists="".join(dl.xpath(".//p[@class='tel_shop']/text()").getall()).split()
            for list in lists:
                if '室' in list:
                    #户型
                   item['room_type']=list
                elif '㎡' in list:
                    #面积
                   item['area']=list
                elif '层' in list:
                    #楼层
                   item['floor']=list
                elif '向' in list:
                    #朝向
                   item['orientation']=list
                elif '年' in list:
                    #建筑时间
                   item['build_year']=list

            #小区名字
            village_name = dl.xpath(".//p[@class='add_shop']/a/@title").get()
            item['village_name'] = village_name

            #地址
            address = dl.xpath(".//p[@class='add_shop']/span/text()").get()
            item['address'] = address

            #万和每平方米的价格
            company_unit = " ".join(dl.xpath(".//dd[@class='price_right']/span/text()").getall()).split()
            #总价
            money = dl.xpath(".//dd[@class='price_right']/span/b/text()").get()
            total=money+company_unit[0]
            item['total'] = total

            #每平方米的价格
            unit = company_unit[1]
            item['unit']=unit

            yield item
        # 下一页的链接
        next_link = response.urljoin(response.xpath("//div[@class='page_al']/p[2]/a/@href").get())
        #如果不为转跳到下一页
        if next_link:
            yield scrapy.Request(url=next_link, callback=self.parse_esfhouse, meta={"info": (province, city)})


    # 对于租房页面的解析
    def parse_zuhouse(self,response):
        print("-------------------------------------------------对于租房页面的解析--------------------------------------------------")
        item=ZufItem()
        province, city = response.meta.get("info")
        item['province']=province
        item['city']=city
        #获取每个租房的dl
        dls=response.xpath("//div[@class='houseList']/dl")
        for dl in dls:
            #获取租房的标题
            title=dl.xpath(".//p[@class='title']/a/text()").get()
            item['title']=title

            # 房详细信息的链接
            housenews_url = response.urljoin(dl.xpath(".//p[@class='title']/a/@href").get())
            item['housenews_url'] = housenews_url

            # 租房类型
            lists =" ".join(dl.xpath(".//p[contains(@class,'font15')]/text()").getall()).split()
            for list in lists:
                if '租' in list:
                    #出租的类型
                    item['zutype'] = list
                elif '㎡' in list:
                    #面积
                    item['area'] = list
                elif '朝' in list:
                    #朝向
                    item['orientation'] = list
                else:
                    #户型
                    item['room_type'] = list

            # 地址
            address = '/'.join(dl.xpath(".//p[contains(@class,'gray6')]/a/span/text()").getall())
            item['address']=address

            # 月租
            money_a = dl.xpath(".//p[contains(@class,'alingC')]/span/text()").get()
            money_b = dl.xpath(".//p[contains(@class,'alingC')]/text()").get()
            money=money_a+money_b
            item['money'] = money

            yield item
       # 下一页的链接
        next_link = response.urljoin(response.xpath("//div[@class='fanye']/a[6]/@href").get())

        #如果不为转跳到下一页
        if next_link:
            yield scrapy.Request(url=next_link, callback=self.parse_esfhouse, meta={"info": (province, city)})


    # 对于商铺出租页面的解析
    def parse_shop_zu(self,response):
        print("-------------------------------------------------对于商铺出租页面的解析--------------------------------------------------")
        item = ShopZuItem()
        province, city = response.meta.get("info")
        #获取商铺出租所有dl
        dls=response.xpath("//div[contains(@class,'shop_list')]/dl")

        if dls:
            item['province'] = province
            item['city'] = city
            for dl in dls:
                #获取商铺出租的标题
                title=dl.xpath(".//h4[@class='clearfix']/a/@title").get()
                item['title']=title

                #商铺详细信息的链接
                shopzunews_url=response.urljoin(dl.xpath(".//h4[@class='clearfix']/a/@href").get())
                item['shopzunews_url'] = shopzunews_url

                # 商铺所在标志
                sign = dl.xpath(".//p[@class=' add_shop']/a/@title").get()
                item['sign'] = sign

                # 地址
                address =dl.xpath(".//p[@class=' add_shop']/span/text()").get()
                item['address'] = address

                lists = ' '.join(dl.xpath(".//p[@class='tel_shop']/text()").getall()).split()
                # 商铺出租类型
                shop_type = lists[0]
                item['shop_type'] = shop_type

                # 楼层
                floor = lists[1]
                item['floor'] = floor

                # 面积
                area = lists[2]
                item['area'] = area

                # 月租
                money = "".join(dl.xpath(".//dd[@class='price_right']/span[@class='red']//text()").getall()).strip()
                item['money'] = money

                # 每平米每天多少钱
                day_money =dl.xpath("..//dd[@class='price_right']/span[not(@class)]/text()").get()
                item['day_money'] = day_money

                yield  item

            # 下一页的链接
            next_link = response.urljoin(response.xpath("//div[@class='page_al']/p[1]/a/@href").get())

            # 如果不为转跳到下一页
            if next_link:
                yield scrapy.Request(url=next_link, callback=self.parse_shop_zu, meta={"info": (province, city)},dont_filter=True)


    # 对于商铺出售页面的解析
    def parse_shop_shou(self,response):
        print("-------------------------------------------------对于商铺出售页面的解析--------------------------------------------------")
        item = ShopShouItem()
        province, city = response.meta.get("info")
        # 获取商铺出售所有dl
        dls = response.xpath("//div[contains(@class,'shop_list')]/dl")

        if dls:
            item['province'] = province
            item['city'] = city
            for dl in dls:
                # 获取商铺出租的标题
                title = dl.xpath(".//h4[@class='clearfix']/a/@title").get()
                item['title'] = title

                # 商铺详细信息的链接
                shopshounews_url = response.urljoin(dl.xpath(".//h4[@class='clearfix']/a/@href").get())
                item['shopshounews_url'] = shopshounews_url

                # 商铺所在标志
                sign = dl.xpath(".//p[@class=' add_shop']/a/@title").get()
                item['sign'] = sign

                # 地址
                address = dl.xpath(".//p[@class=' add_shop']/span/text()").get()
                item['address'] = address

                lists = ' '.join(dl.xpath(".//p[@class='tel_shop']/text()").getall()).split()
                # 商铺出租类型
                shop_type = lists[0]
                item['shop_type'] = shop_type

                # 楼层
                floor = lists[1]
                item['floor'] = floor

                # 面积
                area = lists[2]
                item['area'] = area

                # 总价
                total = "".join(dl.xpath(".//dd[@class='price_right']/span[@class='red']//text()").getall()).strip()
                item['total'] = total

                # 每平米的价格
                unit = dl.xpath("..//dd[@class='price_right']/span[not(@class)]/text()").get()
                item['unit'] = unit

                yield item

            # 下一页的链接
            next_link = response.urljoin(response.xpath("//div[@class='page_al']/p[1]/a/@href").get())

            # 如果不为转跳到下一页
            if next_link:
                yield scrapy.Request(url=next_link, callback=self.parse_shop_shou, meta={"info": (province, city)},
                                     dont_filter=True)


    #检测报错信息
    def errback_httpbin(self,failure):
        # 日志记录所有的异常信息
        self.logger.error(repr(failure))
        # 假设我们需要对指定的异常类型做处理，
        # 我们需要判断异常的类型

        if failure.check(HttpError):
            # HttpError由HttpErrorMiddleware中间件抛出
            # 可以接收到非200 状态码的Response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # 此异常由请求Request抛出
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request

            self.logger.error('TimeoutError on %s', request.url)