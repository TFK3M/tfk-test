#!/usr/bin/python

from cc import *
import func
import mysql
import os
import sys
import threading
import MySQLdb
import time
import math
import urllib

#获取目标时间
nowtime = time.localtime()

#判断当前时间段
StartDate = str(nowtime.tm_year) + '-' + str(nowtime.tm_mon) + '-' + str(nowtime.tm_mday)

'''
入参：[ID,ID,ID]
出参：'shID,shID,szID'
'''
def comJoin(sList):
  sStr = ""
  for s in sList:
    if s[0] == '0':
      sStr = sStr + URL_TAIL_SZ_SINA + s + ','
    else:
      sStr = sStr + URL_TAIL_SH_SINA + s + ','
  return sStr[0:len(sStr) - 1]

def dealSinaDataM(s):
  sList = s.split(',')
  if len(sList) > 3:
    #判断是否停牌
    if sList[1] == '0.00':
      del s
    else:
      return sList[3]
  else:
    del s

def dealSinaDataD(s):
  sList = s.split(',')
  if len(sList) > 3:
    #判断是否停牌
    if sList[1] == '0.00':
      del s
    else:
      return sList[3:6]
  else:
    del s

def dealDealTime(s):
  return int(time.mktime(time.strptime(StartDate + s,'%Y-%m-%d %H:%M:%S')))

AmStart,AmEnd,FmStart,FmEnd = map(dealDealTime, DEAL_TIME)
RestStart,RestEnd = map(dealDealTime, REST_TIME)

class StockInfo(threading.Thread):
  def __init__(self, stock = None):
    threading.Thread.__init__(self)
    self.db =  mysql.mysql()
    
    if stock == None:
      self.stock = 'sz000001'
    else:
      self.stock = stock

  def run(self):
    while True:
      self.summaryMin()

      #进入午盘收盘或者当日收盘则结束进程
      if (time.time() >= RestStart and time.time() <= RestEnd) or (time.time() >= FmEnd):
        #插入日线
        if (time.time() >= FmEnd):
          self.summaryDay()
        break
      else:
        #暂停30分钟
        Now = time.time()
        Inteval = THREAD_INTEVAL-(Now - AmStart)%THREAD_INTEVAL
        time.sleep(Inteval)

  def summaryMin(self):
    self.db.connect()
    url = URL_HEAD_SINA + self.stock
    urldoc = urllib.urlopen(url).read()
    urldoc = urldoc.split(';')
    urldoc.pop()
    urldocList = map(dealSinaDataM, urldoc)

    stockPriceInfo = dict(zip(self.stock.split(","),urldocList))
    self.db.insertMin(stockPriceInfo)
    self.db.discon()

  def summaryDay(self):
    self.db.connect()
    url = URL_HEAD_SINA + self.stock
    urldoc = urllib.urlopen(url).read()
    urldoc = urldoc.split(';')
    urldoc.pop()
    urldocList = map(dealSinaDataD, urldoc)

    stockPriceInfo = dict(zip(self.stock.split(","),urldocList))
    self.db.insertDay(stockPriceInfo)
    self.db.discon()

def checkSystem():
  #清楚过期数据
  db = mysql.mysql()
  db.connect()
  db.deleteUselessData()
  db.discon()
  
  #获取当前时间戳
  Now = time.time()
  #上午开盘前
  if Now < AmStart:
    Inteval = AmStart - Now
    print "Wait For Am Start!Left:" + str(Inteval)
    Inteval = Inteval + THREAD_INTEVAL
  #上午开盘中
  elif Now < AmEnd:
    Inteval = THREAD_INTEVAL-(Now - AmStart)%THREAD_INTEVAL
    print "Aming...Here We Go!"
  #下午开盘前
  elif Now < FmStart:
    Inteval = FmStart - Now
    print "Wait For Fm Start!Left:" + str(Inteval)
    Inteval = Inteval + THREAD_INTEVAL
  #下午开盘中
  elif Now < FmEnd:
    Inteval = THREAD_INTEVAL-(Now - FmStart)%THREAD_INTEVAL
    print "Fming...Here We Go!"
  #收盘
  else:
    print "Game Over!Enjoy Your Life!"
    sys.exit()

  #等待
  time.sleep(Inteval)

if __name__ == '__main__':
  '''
  每日CHECK
  1.日线数据是否更新到位
  2.30分钟线数据是否更新到位
  '''
  checkSystem()
  
  #获取所有股票信息
  db = mysql.mysql()
  db.connect()
  stockList = db.getAllStockInfo()
  db.discon()
  stockIdList = list(zip(*stockList)[0])
  
  #每一个线程包含的股票数
  everyStocks = int(math.ceil(float(len(stockList))/float(THREAD_COUNT)))

  stocksT = []
  for i in range(THREAD_COUNT):
      stocksT.append(stockIdList[(i+1-1)*everyStocks:(i+1)*everyStocks])

  stocksT = map(comJoin, stocksT)
  
  tList = []
  for i in range(THREAD_COUNT):
    newT = StockInfo(stocksT[i])
    tList.append(newT)
    newT.setName("T" + str(i+1))
    newT.start()
    
  for t in tList:
    t.join()
  
  sys.exit()
