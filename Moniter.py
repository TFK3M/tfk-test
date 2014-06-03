# encoding:utf-8
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
import datetime

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

def dealSinaData(s):
  sList = s.split(',')
  if len(sList) > 3:
    return sList[3]
  else:
    del s
'''
Deal Moniter
'''
class DealMoniter(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.db =  mysql.mysql()
    self.db.connect()
    
    dealInfo = self.db.getDealMonitInfo()
    self.dealInfo = dict(dealInfo)
    self.stockList = list(zip(*dealInfo)[0])
    self.moniterRec = dict(zip(self.stockList,[0.1] * len(self.stockList)))

    self.db.discon()

    self.initAvg()

  '''
  INIT THE MONIT STOCKS AVG INFO
  '''
  def initAvg(self):
    self.db.connect()
    self.stockAvg = {}
    for stock in self.stockList:
      avgInfo = self.db.getAvgInfoById(stock, "1")
      self.stockAvg[stock] = avgInfo       
    self.db.discon()
        
  def run(self):
    for i in range(1000):
      self.doProcess()
      time.sleep(MONITER_INTEVAL)

  def doProcess(self):
    self.db.connect()
    url = URL_HEAD_SINA + comJoin(self.stockList)
    urldoc = urllib.urlopen(url).read()
    urldoc = urldoc.split(';')
    urldoc.pop()
    urldocList = map(dealSinaData, urldoc)
    stockPriceInfo = dict(zip(self.stockList,urldocList))
    
    #对比均线信息,判断机会
    for (sid,cur) in stockPriceInfo.items():
      if abs((float(cur) - float(self.moniterRec[sid]))/float(self.moniterRec[sid]) * 100) >= 1 :
        self.checkDeal(float(cur), float(self.dealInfo[sid]), float(self.stockAvg[sid][1]), float(self.stockAvg[sid][2]), sid)
    self.db.discon()

  '''
  CHECK IF IS THE DEAL POINT
  '''
  def checkDeal(self, cur, cost, minu, day, sid):
    
    #FIRST MARGIN PRICE
    firstM = cost * 0.97
    if cur <= firstM:
      print "%s CUR PRICE:%.2f\nFIRST MARGIN PRICE:%.2f\n" % (sid, cur, firstM)
    
    #SECOND MARGIN PRICE
    secondM = cost * 0.94
    if cur <= secondM:
      print "%s CUR PRICE:%.2f\nSECOND MARGIN PRICE:%.2f\n" % (sid, cur, secondM)

    #STOP LOSS PRICE
    out = cost * 0.9
    if cur <= out:
      print "%s CUR PRICE:%.2f\nSTOP LOSS PRICE:%.2f\n" % (sid, cur, out)
    
    #FIRST PROFIT PRICE
    firstP = minu
    if cur <= secondM:
      print "%s CUR PRICE:%.2f\nFIRST PROFIT PRICE:%.2f\n" % (sid, cur, firstP)

    #SECOND PROFIT PRICE
    secondP = minu * 2 - cost
    if cur <= secondM:
      print "%s CUR PRICE:%.2f\nSECOND PROFIT PRICE:%.2f\n" % (sid, cur, secondP)

    self.moniterRec[sid] = cur

'''
OppMoniter

monitFile = open('MonitStock.csv','w')
for monitStock in monitStockInfo:
  monitFile.write(",".join(map(lambda s:str(s),monitStock)) + "\n")
monitFile.close()
        
'''
class OppMoniter(threading.Thread):
  def __init__(self, stock = None):
    threading.Thread.__init__(self)
    self.db =  mysql.mysql()
    self.db.connect()
    
    if stock == None:
      self.stock = 'sz000001'
      self.stockList = ['000001']
    else:
      self.stock = stock
      self.stockList = map(lambda s:s[2:], self.stock.split(","))
      self.stockOpp = dict(zip(self.stockList, [0] * len(self.stockList)))

    #初始化均线信息
    self.initAvg()
    
    self.db.discon()

  '''
  初始化该线程的均线信息
  '''
  def initAvg(self):
    avgInfo = self.db.getMonitAvgInfo()
    self.stockAvg = {}
    for avg in avgInfo:
      if avg[0] in self.stockList:
        self.stockAvg[avg[0]] = avg

  '''
  初始化机会文件
  '''
  def writeOppData(self, s):
    baseDir = os.getcwd()
    oppFileDir = os.path.join(baseDir, MONITER_FILE)
    oppFileName = "OppData" + str(datetime.date.today()) + ".txt"
    oppFile = os.path.join(oppFileDir, oppFileName)
    monitFile = open(oppFile,'a+')
    monitFile.write(s)
    monitFile.close()
    
  '''
  判断是否是机会
  '''
  def checkOpp(self, cur, minu, day, sid):
    if float(cur) == 0:
      return
    
    if cur and minu and day:
      dayPlv = (float(cur) - float(day)) / float(day) * 100
      minPlv = (float(minu) - float(cur)) / float(minu) * 100
      oppValue = minPlv - dayPlv
      
      if (abs(float(float(self.stockOpp[sid])) - oppValue)) >= 1:
        
        if oppValue >= LOPP_MIN:
          print "LARGE OPP %s:%s" % (sid,cur)
          print "[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue)
          self.writeOppData("%s LARGE  OPP %s:%s" % (str(datetime.datetime.today()), sid,cur))
          self.writeOppData("[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue))
        elif oppValue >= MOPP_MIN:
          print "MIDDLE OPP %s:%s" % (sid,cur)
          print "[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue)
          self.writeOppData("%s MIDDLE OPP %s:%s" % (str(datetime.datetime.today()), sid,cur))
          self.writeOppData("[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue))
        elif oppValue >= SOPP_MIN:
          print "SMALL OPP %s:%s" % (sid,cur)
          print "[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue)
          self.writeOppData("%s SMALL  OPP %s:%s" % (str(datetime.datetime.today()), sid,cur))
          self.writeOppData("[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue))

        self.stockOpp[sid] = oppValue
    else:
      pass

  def run(self):
    for i in range(1000):
      self.doProcess()
      time.sleep(MONITER_INTEVAL)

  def doProcess(self):
    self.db.connect()
    url = URL_HEAD_SINA + self.stock
    urldoc = urllib.urlopen(url).read()
    urldoc = urldoc.split(';')
    urldoc.pop()
    urldocList = map(dealSinaData, urldoc)
    stockPriceInfo = dict(zip(self.stockList,urldocList))
    
    #对比均线信息,判断机会
    for (sid,cur) in stockPriceInfo.items():
      if sid in self.stockAvg.keys():
        self.checkOpp(cur, self.stockAvg[sid][1], self.stockAvg[sid][2], sid)
    self.db.discon()

if __name__ == '__main__':

  #GET ALL THE MONIT STOCK INFO
  db = mysql.mysql()
  db.connect()
  stockList = db.getMoniterStockInfo()
  db.discon()
  
  stockIdList = list(zip(*stockList)[0])
  
  #THE COUNT OF STOCKS IN EVERY THREAD
  everyStocks = int(math.ceil(float(len(stockList))/float(MONITER_TCOUNT)))

  stocksT = []
  for i in range(MONITER_TCOUNT):
      stocksT.append(stockIdList[(i+1-1)*everyStocks:(i+1)*everyStocks])

  stocksT = map(comJoin, stocksT)

  tList = []

  '''
  #START DEAL MONITER
  print "DEAL MONITER>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  dealMoniter = DealMoniter()
  tList.append(dealMoniter)
  dealMoniter.start()
  '''

  #print "OPP MONITER>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  #START OPP MONITER
  for i in range(MONITER_TCOUNT):
    newT = OppMoniter(stocksT[i])
    tList.append(newT)
    newT.start()
  
  for t in tList:
    t.join()

  raw_input("Moniter over!Press Any Key To Quit!")
  sys.exit()
