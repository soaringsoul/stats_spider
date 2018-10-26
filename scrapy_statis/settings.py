# -*- coding: utf-8 -*-
from sqlalchemy import create_engine

BOT_NAME = 'scrapy_statis'
SPIDER_MODULES = ['scrapy_statis.spiders']
NEWSPIDER_MODULE = 'scrapy_statis.spiders'

# 配置mysql, 使用sqlalchemy的creteengine
user = "root"  # mysql用户名
passwd = "adas123456"  # mysql用户密码
host = "localhost"  # mysql ip address

db = "mycrawdata"  # 用于设置数据库名，这个必须提前创建好
charset = 'utf8'  # 编码
mysql_settings = "mysql+pymysql://{user}:{passwd}@{host}/{db}?charset={charset}".format(user=user, passwd=passwd,
                                                                                        host=host, db=db,
                                                                                        charset=charset)
engine = create_engine(mysql_settings)

# 设置数据库表名，在这里填写名字即可，若不存在会自动创建
write_sql_table_name = "stats_gov_cn_data"

"""
设置需要采集的年份，默认为all，即采集所有年份, 
如果要指定年份，输入年份即可，
例如只采集2017年的数据:
year_settings = 2017
"""
year_settings = 2017


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'scrapy_statis (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'scrapy_statis.middlewares.ScrapyStatisSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_statis.middlewares.RandomUserAgentMiddleware': 543,
    # 这里要设置原来的scrapy的useragent为None，否者会被覆盖掉
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}
RANDOM_UA_TYPE = 'random'

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_statis.pipelines.ScrapyStatisPipeline': 300,
}
LOG_LEVEL = 'ERROR'

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
