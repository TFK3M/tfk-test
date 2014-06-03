#!/usr/bin/python

from cc import *
import func
import mysql
import os
import sys
import threading
import MySQLdb


try:
  choose = raw_input("Are you sure to analyse the system?(y/n)\n")
  if choose != "y":
    sys.exit()
  db = mysql.mysql()
  db.connect()
  db.analyseStockOne()
  db.analyseStockTwo()
  db.discon()
  raw_input("Analyse System Success!Press Any Key To Quit!")
    
except Exception,e:
  print e
  sys.exit()

finally:
  pass
