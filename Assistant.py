# encoding:UTF-8
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

def monitOpp(sid, cur, minu, day):
  if float(cur) == 0:
    return
  
  dayPlv = (float(cur) - float(day)) / float(day) * 100
  minPlv = (float(minu) - float(cur)) / float(minu) * 100
  oppValue = minPlv - dayPlv
  
  if oppValue >= LOPP_MIN:
    print "LARGE OPP %s:%s" % (sid,cur)
    print "[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue)
  elif oppValue >= MOPP_MIN:
    print "MIDDLE OPP %s:%s" % (sid,cur)
    print "[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue)
  elif oppValue >= SOPP_MIN:
    print "SMALL OPP %s:%s" % (sid,cur)
    print "[MIN:%.2f DAY:%.2f DIFF:%.2f]\n" % (minPlv,dayPlv,oppValue)
  
  return oppValue

if __name__ == '__main__':
  while True:
    print("")
    command = raw_input("Please Input The Command:")
    command = command.lower()

    #分隔命令
    comList = command.split(" ")
    if len(comList) > 3:
      print "Wrong Command : too many elements!"
      continue
    else:
      #将命令自动扩展到三个元素，如果不足则自动添加空字符串元素
      comList.extend(["" for i in range(2 - len(comList))])
      Cmd,Param = comList

    #主命令是否已定义
    if Cmd not in COMMAND_LIST:
      print "Wrong Command : not defined yet!"
      continue

    '''
    退出命令
    主命令：q:quit
    模式：无
    参数：无
    '''
    if Cmd == "q":
      break;

    '''
    报表操作命令
    主命令：r:report
    参数：
        dealin 将交易数据导入数据库
        dealout 将交易数据报表输出
    '''
    if Cmd == "r":
      if Param == "dealin":
        dealFile = open('DealData.csv','r')
        
        dealInfo = []
        for line in dealFile:
          dealInfo.append(line[0:-1].split(','))
        del dealInfo[0]
        db = mysql.mysql()
        db.connect()
        calcStockInfo = db.insertDeal(dealInfo)
        db.discon()
        print "DealDate import success!"
        
      if Param == "dealout":
        pass

    '''
    入仓计算
    主命令：b:buy
    模式：无
    参数：price
    '''
    if Cmd == "b":
      if Param == "":
        print "Wrong Param : can not be null!"
        continue
      else:
        price = float(Param)
        
      first = price * 0.97
      second = price * 0.94
      out = price * 0.9

      print "Frist in: %.2f" % (first)
      print "Second in: %.2f" % (second)
      print "Out in: %.2f" % (out)
    
    '''
    计算命令:计算当前差额及三级价格
    主命令：c:calc
    模式：无
    参数：id
    '''
    if Cmd == "c":
      if Param == "":
        print "Wrong Param : can not be null!"
        continue

      if "-" in Param:
        sid, mode = Param.split("-")
      else:
        sid = Param
        mode = "1"
      
      if sid[0] == "0":
        url = URL_HEAD_SINA + URL_TAIL_SZ_SINA + sid
      elif sid[0] == "6":
        url = URL_HEAD_SINA + URL_TAIL_SH_SINA + sid
      else:
        print "Wrong Param : not true!"
        continue

      db = mysql.mysql()
      db.connect()
      calcStockInfo = db.getAvgInfoById(sid, mode)
      db.discon()
      
      urldoc = urllib.urlopen(url).read()
      urldoc = urldoc.split(';')
      urldoc.pop()
      
      sid,minu,day = calcStockInfo
      cur = urldoc[0].split(',')[3]
      
      dayPlv = (float(cur) - float(day)) / float(day) * 100
      minPlv = (float(minu) - float(cur)) / float(minu) * 100
      oppValue = minPlv - dayPlv
      
      LOppValue = (float(2) - float(LOPP_MIN*0.01))/(float(1/minu) + float(1/day))
      MOppValue = (float(2) - float(MOPP_MIN*0.01))/(float(1/minu) + float(1/day))
      SOppValue = (float(2) - float(SOPP_MIN*0.01))/(float(1/minu) + float(1/day))

      print "Now:%.2f Min:%.2f Day:%.2f" % (float(cur), minPlv, dayPlv)
      print "Current OppValue is %.2f" % (oppValue)
      print "LOppValue is %.2f" % (LOppValue)
      print "MOppValue is %.2f" % (MOppValue)
      print "SOppValue is %.2f" % (SOppValue)
      
    '''
    监控命令
    主命令：m:monit
    模式：1-监测；2-制作监测文件；
    参数：time(s)
    '''
    if Cmd == "m":
      if Param == "2":
        db = mysql.mysql()
        db.connect()
        monitStockInfo = db.getMonitAvgInfo()
        db.discon()

        monitFile = open('MonitStock.csv','w')
        for monitStock in monitStockInfo:
          monitFile.write(",".join(map(lambda s:str(s),monitStock)) + "\n")
        monitFile.close()
        print "MonitStock.csv make success!"
        continue

      #监视间隔秒数
      inteval = 10
      #从MonitStock.csv获取监控股票信息
      monitFile = open('MonitStock.csv','r')

      monitStocks = []
      for line in monitFile:
        monitStocks.append(line[0:-1].split(','))
      #del monitStocks[0]

      stockIdList = list(zip(*monitStocks)[0])
      minuList = list(zip(*monitStocks)[1])
      dayList = list(zip(*monitStocks)[2])

      minPriceInfo = dict(zip(stockIdList,minuList))
      dayPriceInfo = dict(zip(stockIdList,dayList))
      
      stocksT = comJoin(stockIdList)
      
      for i in range(1):
        
        url = URL_HEAD_SINA + stocksT
        urldoc = urllib.urlopen(url).read()
        urldoc = urldoc.split(';')
        urldoc.pop()
        urldocList = map(dealSinaData, urldoc)
        curPriceInfo = dict(zip(stockIdList,urldocList))
        
        #对比均线信息,判断机会
        largestOpp = -100
        largestSid = ""
        for (sid,cur) in curPriceInfo.items():
          oppValue = monitOpp(sid,cur,minPriceInfo[sid], dayPriceInfo[sid])
          if oppValue > largestOpp:
            largestOpp = oppValue
            largestSid = sid
        print "Sid:%s\nValue:%.2f" % (largestSid, largestOpp)
        #time.sleep(inteval)

    
