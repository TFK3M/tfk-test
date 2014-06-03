# encoding:UTF-8

#SYSTEM INFO
DEBUG = False
PRINTSQL = False

#交易时间段
DEAL_TIME = [' 09:30:00',' 11:30:00',' 13:00:00',' 15:00:00']

#收市时间
REST_TIME = [' 11:30:00',' 13:00:00']

'''
InitSystem使用
INIT_MODE:1=全部初始化；2=通过文件数据初始化
'''
INIT_MODE = '2'
INIT_DIR = 'InitData'

'''
AM9PM15使用
THREAD_INTEVAL:抓取数据间隔时间
THREAD_COUNT:启动线程数
'''
THREAD_INTEVAL = 60*30
THREAD_COUNT = 20

'''
MONITER使用
'''
MONITER_INTEVAL = 1
MONITER_TCOUNT = 1

LOPP_MIN = 13
MOPP_MIN = 10
SOPP_MIN = 7

MONITER_FILE = 'OppData'

'''
Assistant使用
'''
COMMAND_LIST = ['q','m','r','c','b']

'''
SINA URL INFO
SH EXAMPLE:http://hq.sinajs.cn/list=sh600001
SZ EXAMPLE:http://hq.sinajs.cn/list=sz000001
DATA STRUCT:
    0：股票名字
    1：今日开盘价
    2：昨日收盘价
    3：当前价格
    4：今日最高价
    5：今日最低价
'''
URL_HEAD_SINA = r"http://hq.sinajs.cn/list="
URL_TAIL_SH_SINA = "sh"
URL_TAIL_SZ_SINA = "sz"

'''
YAHOO URL INFO
SH EXAMPLE:http://table.finance.yahoo.com/table.csv?s=600001.ss
SZ EXAMPLE:http://table.finance.yahoo.com/table.csv?s=000001.sz
'''
URL_HEAD_YAHOO = r'http://table.finance.yahoo.com/table.csv?s='
URL_TAIL_SH_YAHOO = r'.ss'
URL_TAIL_SZ_YAHOO = r'.sz'

'''
DB CONNECT INFO
'''
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_DATABASE = "tfk"

