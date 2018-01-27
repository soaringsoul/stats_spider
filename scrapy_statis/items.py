# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    year = scrapy.Field()
    prov = scrapy.Field()
    prov_code = scrapy.Field()
    prov_url = scrapy.Field()

    city = scrapy.Field()
    city_code = scrapy.Field()
    city_stats_code = scrapy.Field()
    city_url = scrapy.Field()

    district = scrapy.Field()
    district_code = scrapy.Field()
    district_stats_code = scrapy.Field()
    district_url = scrapy.Field()
    district_tmp_code = scrapy.Field()

    town = scrapy.Field()
    town_code = scrapy.Field()
    town_stats_code = scrapy.Field()
    town_url = scrapy.Field()

    village_info = scrapy.Field()
    village = scrapy.Field()
    village_type = scrapy.Field()
    village_stats_code = scrapy.Field()










