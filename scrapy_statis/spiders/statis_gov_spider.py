import re
import time
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

from scrapy_statis.items import Item
from bs4 import BeautifulSoup


class StatisGovSpider(CrawlSpider):
    name = 'stats_spider'
    allowed_domains = ['stats.gov.cn']
    start_urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/']
    rules = (
        # 获取各年份统计数据链接
        Rule(LinkExtractor(allow=(r'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index\.html')),
             callback='parse_province'),)

    def parse_province(self, response):
        """
        :param response: 2009-2016年各年份各省的链接
        :return: 【年份、省,省代码、省链接】四个维度
        """
        print('起始页：%s' % response.url)
        # 定义一个空列表，保存本级解析页面获取到的【年份、省,省代码、省链接】，items_1元素是一个各省数据的列表
        items_1 = []
        while response.status != 200:
            time.sleep(10)
            # print(response.status)
            self.parse_main(response)
        for prov in LinkExtractor(allow=(r'tjyqhdmhcxhfdm/2016/\d\d\.html')).extract_links(response):
            """
            实例化items.py中定义的item！
            注意：必须在循环中实例化！
            """
            item = Item()
            url = prov.url
            text = prov.text
            item['year'] = url[-12:-8]
            item['prov'] = text
            item['prov_code'] = url[-7:-5]
            item['prov_url'] = url
            # print('当前年份:【item[year]】\n当前省:【item[prov]】'.format(item=item))
            items_1.append(item)
            print(item['prov_url'])

        for item_tmp in items_1:
            print(item_tmp['prov'])
            yield Request(item_tmp['prov_url'], meta={'item_1': item_tmp}, callback=self.parse_city,
                          dont_filter=True)

    def parse_city(self, response):
        """
        :param response: 解析各省城市列表
        :return 【城市名, 城市代码, 城市区划代码, 城市链接】四个维度
        """
        # 接收上级页面解析数据
        item_1 = response.meta['item_1']
        # 定义一个空列表，接收parse_prov中解析的数据，并保存本级页面解析的数据,items_2元素是一个各城市数据的列表
        items_2 = []
        # 获取当前省城市列表text
        text = response.xpath('/html/body/table[2]/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr/td/table') \
                [0].extract()
        # 使用正则表达式解析各城市数据，保存在items_2中
        pat = r'<a href="(\d{2})/(\d{4})\.html">(\d{12})</a></td><td><a href="\d{2}/\d{4}\.html">([\u4e00-\u9fa5]+)</a>'
        for prov_code, city_code, city_stats_code, city in re.findall(pat, text):
            # 实例化本层的item, 注意：必须在循环中实例化！！！
            item = Item()
            # 将上级页面的item_1中的【年份、省,省代码、省链接】传递给当前item：
            for key in item_1:
                item[key] = item_1[key]
            # 将本级页面解析出的【城市名, 城市代码, 城市区划代码, 城市链接】放入item字典
            item['city'] = city
            item['city_code'] = city_code
            item['city_stats_code'] = city_stats_code
            item['city_url'] = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/%s/%s/%s.html' \
                               % (item['year'], item['prov_code'], item['city_code'])
            items_2.append(item)

        for item in items_2:
            print('当前城市：%s' % item['city'])
            print('当前城市url：%s' % item['city_url'])
            yield Request(item['city_url'], meta={'item_2': item}, callback=self.parse_district, dont_filter=True)

    def parse_district(self, response):
        print(response.url)


        """
        :param response: 解析各城市区县列表
        :return: 【区县名，区县行政代码，区县区划代码、区县临时编号，区县链接】
        """
        # 接收上级页面解析数据
        item_2 = response.meta['item_2']
        print('接收上级页面解析数据：%s' % item_2)
        # 定义一个空列表，接收parse_city中解析的数据，并保存本级页面解析的数据,items_3元素是一个各城市数据的列表
        items_3 = []
        # 获取区县列表text
        soup = BeautifulSoup(response.text, 'lxml')

        district_dict = {}
        for link in soup.find_all(href=re.compile("\d\d/\d{1,10}\.html")):
            href = link['href']
            district_dict[href] = {'code': '', 'name': '' }

        for link in soup.find_all(href=re.compile("\d\d/\d{1,10}\.html")):
            href = link['href']
            district = link.string
            m = re.search('[\u4e00-\u9fa5]', district)
            if m is not None:
                district_dict[href]['name'] = district
            else:
                district_dict[href]['code'] = district

        for href, district_info in district_dict.items():
            tmpcode, district_code = href.strip('.html').split(r'/')
            district, stats_code = district_info['name'], district_info['code']
            item = Item()
            """
            将上级页面中的item传递给本层item，包括：
            【年份、省,省代码、省链接】+ 【城市名, 城市代码, 城市区划代码, 城市链接】
            """
            for key in item_2:
                item[key] = item_2[key]
            # 解析本级页面【区县名，区县行政代码，区县区划代码、区县临时编号，区县链接】并传递给item
            item['district'] = district
            item['district_code'] = district_code
            item['district_stats_code'] = stats_code
            item['district_tmp_code'] = tmpcode
            item['district_url'] = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/%s/%s/%s/%s.html'\
                                       % (item['year'], item['prov_code'], tmpcode, item['district_code'])

            items_3.append(item)

        for item in items_3:
            if len(item['district_code']) == 6:
                yield Request(item['district_url'], meta={'item_3': item}, callback=self.parse_town, dont_filter=True)
            else:
                # 对于类似东莞等无区县城市的处理
                item['town_code'] = item['district_code']
                item['town'] = item['district']
                item['town_stats_code'] = item['district_stats_code']
                item['town_code'] = item['district_code']
                item['district_code'] = "%s00" % item['city_code']
                item['town_url'] = item['district_url']
                yield Request(item['district_url'], meta={'item_4': item}, callback=self.parse_village, dont_filter=True)


    def parse_town(self, response):
        """
        :param response: 解析各区县下各乡镇或者街道办事处列表
        :return:【乡镇名或办事处名，town行政代码、town统计区划代码、town临时代码】
        """
        # 定义一个字典对象item_3接收上级页面解析数据
        item_3 = response.meta['item_3']
        print(item_3)
        text = response.xpath('/html/body/table[2]/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr/td/table') \
                [0].extract()
        print(text)
        pat = r'<a href="(\d\d)/(\d{9})\.html">(\d{12})</a></td><td><a href="\d\d/\d{9}\.html">([\u4e00-\u9fa5]+)</a>'
        for town_tmp_code, town_code, town_stats_code, town in re.findall(pat, text):

            # 实例化item
            item = Item()
            # 将上级页面解析结果传递给本层item
            for key in item_3:
                item[key] = item_3[key]
            # 解析本级页面数据
            item['town'] = town
            item['town_code'] = town_code
            item['town_stats_code'] = town_stats_code
            # 生成下级页面解析链接
            item['town_url'] = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/%s/%s/%s/%s/%s.html'\
                               % (item['year'], item['prov_code'], item['district_tmp_code'],
                                  town_tmp_code, item['town_code'])

            yield Request(item['town_url'], meta={'item_4': item}, callback=self.parse_village, dont_filter=True)

    def parse_village(self, response):
        """
        :param response: 解析最后一级社区列表
        :return: 【社区名，社区城乡划分代码、社区行政区划代码】
        """
        item_4 = response.meta['item_4']

        text = response.xpath('/html/body/table[2]/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr/td/table')[0].extract()

        item = Item()
        for key in item_4:
            item[key] = item_4[key]

        item['village_info'] = text

        yield item








