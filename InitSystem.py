#!/usr/bin/python

from cc import *
import func
import mysql
import os
import sys
import threading
import time
import MySQLdb


try:
  choose = raw_input("Are you sure to init the system?(y/n)\n")
  if choose != "y":
    sys.exit()
    
  db = mysql.mysql()
  db.connect()
  if INIT_MODE == '1':
    stockList = db.getInitStockInfo()
  else:
    stockList = func.getFileStockInfo()

  #db.initStockById(['000002',None,''])
  #print stockList[0:10]
  #sys.exit()
  #for stock in stockList[0:1]:
  #  db.initStockById(stock)
  ##  print "sdfsdf"
  #db.initStockById(['600000',None,''])
  #print stockList
  #sys.exit()
  
  for stock in stockList:
    db.initStockById(stock)
    
  db.discon()
  raw_input("System Init Success!\nPress Any Key To Quit..." )
    
  
    
except Exception,e:
  print e
  sys.exit()

finally:
  pass
