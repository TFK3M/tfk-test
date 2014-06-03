#!/usr/bin/python

from cc import *
import func
import os
import sys
import threading
import urllib
import MySQLdb
import time

def getFileStockInfo():
    baseDir = os.getcwd()
    stockFileDir = os.path.join(baseDir, INIT_DIR)
    stockList = map(lambda s: os.path.splitext(s)[0],os.listdir(stockFileDir))
    stockList = zip(stockList, [''] * len(stockList), [''] * len(stockList))
    return stockList

'''
由于YAHOO的安全保护机制，需要把数据文件手动下载
'''
def getFileStockData(stockid):
    if DEBUG:
        print "getFileStockData start:\n" + stockid
    baseDir = os.getcwd()
    stockFileDir = os.path.join(baseDir, INIT_DIR)
    stockFilePath = os.path.join(stockFileDir, stockid + ".csv")
    stockFile = open(stockFilePath)
    stockdata = stockFile.read()
    stockFile.close()
    
    stockdata = stockdata.split('\n')
    del stockdata[0]
    
    if DEBUG:
        print "getFileStockData success!"
    
    return stockdata

def getYahooStockData(stockid, fromdate = None, todate = None):
    
    #开始日期
    if fromdate == None:
        urlFrom = '&a=' + str(time.localtime().tm_mon - 1) \
                + '&b=' + str(time.localtime().tm_mday) \
                + '&c=' + str(time.localtime().tm_year - 2)
    else:
        dateInfoF = str(fromdate).split('-')

	urlFrom = '&a=' + str(int(dateInfoF[1])-1) \
                    + '&b=' + dateInfoF[2] \
                    + '&c=' + dateInfoF[0]

    #结束日期
    if todate == None:
        urlTo = '&d=' + str(time.localtime().tm_mon - 1) \
                + '&e=' + str(time.localtime().tm_mday) \
                + '&f=' + str(time.localtime().tm_year)
    else:
        dateInfoT = str(urlTo).split('-')

	urlTo = '&d=' + str(int(dateInfoT[1])-1) \
                + '&e=' + dateInfoT[2] \
                + '&f=' + dateInfoT[0]
	
    if stockid[0] == '0':
        url = URL_HEAD_YAHOO + stockid + URL_TAIL_SZ_YAHOO + urlFrom + urlTo
    else:
        url = URL_HEAD_YAHOO + stockid + URL_TAIL_SH_YAHOO + urlFrom + urlTo

    if DEBUG:
        print "getYahooStockData start:\n" + url

    for i in range(1):
        try:
            urllink = urllib.urlopen(url)
            urldoc = urllink.read()
            urllink.close()
            #Date,Open,High,Low,Close,Volume,Adj Close
            stockdata = urldoc.split('\n')
            del stockdata[0]
            if DEBUG:
                print "getYahooStockData success!"
            return stockdata

        except Exception,ex:
            #print Exception,":",ex
            return None

    return ''

def getSinaStockData(stockid):
    if DEBUG:
        print "getSinaStockData start!"
    if stockid[0] == '0':
        url = URL_HEAD_SINA  + stockid
    else:
        url = URL_HEAD_SINA  + stockid

    for i in range(1):
        try:
            urllink = urllib.urlopen(url)
            urldoc = urllink.read()
            urllink.close()
            #Date,Open,High,Low,Close,Volume,Adj Close
            stockdata = urldoc.split('\n')
            
            if DEBUG:
                print "getSinaStockData success!"
            return stockdata

        except:
            return ''

    return ''


'''
只获取最近的500天记录并且算出60、120、250均值
'''
def calcStockAvg(stockinfo):
    if DEBUG:
        print "calcStockAvg start!"
    #先获取600条
    if len(stockinfo) >=600:
        stockinfo = stockinfo [0:600]
    
    stockdata = []
    for i in range(len(stockinfo)-1):
        stockinfo[i] = stockinfo[i].split(',')
    
    #网络错误：没有找到数据
    if len(stockinfo[0]) != 7:
        return None
    
    #删除成交量为0的非法数据
    for i in range(len(stockinfo)-1):
        if stockinfo[i][5] != "000":
            stockdata.append(stockinfo[i])
    
    #如果都为0,则返回
    if len(stockdata) == 0:
        return None
    
    #再获取500条
    if len(stockdata) >=500:
        stockdata = stockdata [0:500]
    
    length = len(stockdata)
    closePrice = [float(i) for i in zip(*stockdata)[6]]
    
    for i in range(len(stockdata)):
        if i + 60 + 1 > length:
            #60avg
            stockdata[i].append(0)
        else:
            #60avg
            stockdata[i].append(sum(closePrice[i:i+60])/60)

        if i + 120 + 1 > length:
            #120avg
            stockdata[i].append(0)
        else:
            #120avg
            stockdata[i].append(sum(closePrice[i:i+120])/120)

        if i + 250 + 1 > length:
            #250avg
            stockdata[i].append(0)
        else:
            #250avg
            stockdata[i].append(sum(closePrice[i:i+250])/250)

    if DEBUG:
        print "calcStockAvg success!"

    return stockdata        

