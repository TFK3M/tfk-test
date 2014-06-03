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



if __name__ == '__main__':

  baseDir = os.getcwd()
  oppFileDir = os.path.join(baseDir, MONITER_FILE)
  oppFileName = "OppData" + str(datetime.date.today()) + ".txt"
  oppFile = os.path.join(oppFileDir, oppFileName)
  monitFile = open(oppFile,'a+')
  monitFile.writelines('aa\n')
  monitFile.close()

  monitFile = open(oppFile,'a+')
  monitFile.writelines('bb\n')
  monitFile.close()
