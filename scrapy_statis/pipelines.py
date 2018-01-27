# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pandas as pd
from pandas import DataFrame
import sqlalchemy
from tools import mysql_engine, read_cfg
import time
import re

db_cfg = read_cfg('db.cfg')
engine_mysql = mysql_engine(**db_cfg['localhost'])


class ScrapyStatisPipeline(object):

    def process_item(self, item, spider):
        village_text = item['village_info']

        del item['village_info']

        pat = r'<tr class="villagetr"><td>(\d{12})</td><td>(\d\d\d)</td><td>([\u4e00-\u9fa5]+)</td></tr>'
        tmp_lsts = []
        new_col = ['year', 'prov', 'prov_code', 'city', 'city_code', 'district', 'district_code',
                   'town', 'town_code', 'village', 'village_type', 'village_stats_code', 'city_stats_code',
                   'district_stats_code', 'town_stats_code', 'prov_url', 'city_url', 'district_url',
                   'town_url', 'district_tmp_code']

        for village_stats_code, village_type, village in re.findall(pat, village_text):
            item_tmp = item.copy()
            # print(item_tmp)
            item_tmp['village'] = village
            item_tmp['village_type'] = village_type
            item_tmp['village_stats_code'] = village_stats_code

            tmp_lst = [item_tmp[x] for x in new_col]
            tmp_lsts.append(tmp_lst)

        df = DataFrame(tmp_lsts, columns=new_col)
        print('*'*6,'【%s】' % item['city'], '*'*6,)
        print(df['village'])
        df.to_sql('china_community_db_all_2018', engine_mysql, if_exists='append', index=False)
        return item
