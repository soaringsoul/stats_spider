import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import uuid
import os
from pandas import DataFrame
import pandas as pd
import logging
from sqlalchemy.exc import IntegrityError


def split_dataframe(data, split_num):
    # 把df等分成若干份，split_num代表等分次数，并把每个df放入一个线程中解析数据并入库
    if split_num >= 2:
        length = data.shape[0]
        split_length = int(length/split_num)
        df_list = []
        for i in range(split_num):
            if i < (split_num-1):
                df = data[split_length*i:split_length*(i+1)]
                df_list.append(df)
            else:
                df = data[split_length*i:length]
                df_list.append(df)
    else:
        df_list =[data]
    return df_list


def mysql_engine(**kwargs):
    engine = create_engine("mysql+pymysql://%s:%s@%s/%s?charset=%s"
                               % (kwargs['user'],
                                  kwargs['password'],
                                  kwargs['host'],
                                  kwargs['database'],
                                  kwargs['charset']))
    return engine

def mssql_engine(**kwargs):
    engine = create_engine("mssql+pymssql://%s:%s@%s/%s?charset=%s"
                               % (kwargs['user'],
                                  kwargs['password'],
                                  kwargs['server'],
                                  kwargs['database'],
                                  kwargs['charset']
                                  ), encoding='UTF-8')
    return engine


def read_cfg(filepath):
    db_cfg = configparser.ConfigParser()
    db_cfg.read('%s' % filepath)
    return db_cfg


def df_to_sql_by_chunk(data, tablename, engine, chunksize_num):
    df_length = data.shape[0]
    if df_length > chunksize_num:
        try:
            print('尝试全量写入！')
            data.to_sql(tablename, engine, if_exists='append', index=False, chunksize=20000)
            print('done')
        except:
            print('全量写入失败，将分片写入')
            temp_name = str(uuid.uuid1())
            data.to_csv('%s_temp.csv' % temp_name, encoding='utf8', index=False)
            data_clean = pd.read_csv('%s_temp.csv' % temp_name, chunksize=chunksize_num)
            for df_clean in data_clean:
                try:
                    df_clean.to_sql(tablename, engine, if_exists='append', index=False)
                except IntegrityError as e:
                    print('写入表中已经存在此条记录')
                except Exception as e:
                    logger.exception(e)
                    # 若出错，逐行写入
                    col_names = [x for x in df_clean.columns]
                    for index,df_row in df_clean.iterrows():
                        try:
                            df_temp = DataFrame([df_row], columns=col_names)
                            df_temp.to_sql(tablename, engine, if_exists='append', index=False)
                        except Exception as e:
                            print(e)
            if os.path.exists('%s_temp.csv' % temp_name):
                os.remove('%s_temp.csv' % temp_name)
    else:
        col_names = [x for x in data.columns]
        for index, df_row in data.iterrows():
            print('正在处理写入第---%s---条数据' % index)
            try:
                df_temp = DataFrame([df_row], columns=col_names)
                df_temp.to_sql(tablename, engine, if_exists='append', index=False)
            except IntegrityError as e:
                print('写入表中已经存在此条记录')
            except Exception as e:
                print(e)


def mysql_add_columns_in_batches(engine, db_name, column_name):
    db_session = sessionmaker(bind=engine)
    session = db_session()
    # 获取当前数据库下所有的表名
    sql_get_all_tables = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '%s'" % db_name
    df_tables = pd.read_sql(sql_get_all_tables, engine)
    tables_list = list(df_tables['TABLE_NAME'])
    # 遍历每张表，依次添加新列名
    for table in tables_list:
        sql_add_col = "alter table %s add column %s varchar(500);" % (table, column_name)
        session.execute(sql_add_col)


if __name__ == "__main__":
    db_cfg = read_cfg('db.cfg')
    engine_dw_normal = mysql_engine(**db_cfg['localhost_dw_normal'])
    mysql_add_columns_in_batches(engine_dw_normal, 'dw_normal', 'Term_Of_Validity')