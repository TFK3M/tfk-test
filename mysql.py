#!/usr/bin/python

from cc import *
import func
import time
import MySQLdb

class mysql:

  #conn db info
  host = ''
  user = ''
  password = ''
  db = ''

  __conn = None
  __cursor = None
  
  #init method
  def __init__(self, host = DB_HOST, user = DB_USER, \
               password = DB_PASSWORD, db = DB_DATABASE):
    self.host = host
    self.user = user
    self.password = password
    self.db = db
    pass

  #connect db
  def connect(self):
    self.__conn = MySQLdb.connect(self.host, self.user, self.password, self.db)
    self.__conn.select_db(self.db)
    self.__cursor = self.__conn.cursor()
    if DEBUG:
      print "DB connected!"    

  #discon db
  def discon(self):
    self.__cursor.close()
    self.__conn.close()
    if DEBUG:
      print "DB disconnected!" 

  #select all from db
  def selectAll(self, sql, param = None):
    #if sql has param, then transate it
    if param != None:
      pass

    self.__cursor.execute(sql)
    result = self.__cursor.fetchall()
    if PRINTSQL:
      print "selectAll success:\n" + sql
    return result

  #select one from db
  def selectOne(self, sql, param = None):
    #if sql has param, then transate it
    if param != None:
      pass

    self.__cursor.execute(sql)
    result = self.__cursor.fetchone()
    if PRINTSQL:
      print "selectOne success:\n" + sql
    return result

  def getMoniterStockInfo(self):
    return self.selectAll("SELECT ID,TYPE FROM V_OPP")

  def getInitStockInfo(self):
    return self.selectAll("SELECT ID,UPDATEDATE,NAME FROM STOCKINFO \
                          WHERE UPDATEDATE = '0000-00-00'")

  def getInitStockInfoSh(self):
    return self.selectAll("SELECT ID,UPDATEDATE,NAME FROM STOCKINFO \
                          WHERE UPDATEDATE = '0000-00-00' AND ID >= '600000'")

  def getInitStockInfoSz(self):
    return self.selectAll("SELECT ID,UPDATEDATE,NAME FROM STOCKINFO \
                          WHERE UPDATEDATE = '0000-00-00' AND ID < '600000'")

  def getUpdateStockInfo(self):
    return self.selectAll("SELECT ID,UPDATEDATE,NAME FROM STOCKINFO \
                          WHERE UPDATEDATE < CURDATE() AND UPDATEDATE != '0000-00-00'")
  
  def getAllStockInfo(self):
    return self.selectAll("SELECT ID,UPDATEDATE,NAME FROM STOCKINFO")

  def deleteUselessData(self):
    sqlSzDay = "DELETE FROM SZ_DAY WHERE DATE < ADDDATE(CURDATE(),-730);"
    sqlShDay = "DELETE FROM SH_DAY WHERE DATE < ADDDATE(CURDATE(),-730);"
    sqlSzMin = "DELETE FROM SZ_MIN WHERE TIME < ADDDATE(CURDATE(),-60);"
    sqlShMin = "DELETE FROM SH_MIN WHERE TIME < ADDDATE(CURDATE(),-60);"

    self.__cursor.execute(sqlSzDay)
    self.__cursor.execute(sqlShDay)
    self.__cursor.execute(sqlSzMin)
    self.__cursor.execute(sqlShMin)
    
    self.__cursor.execute("COMMIT;")

  '''
  stockdata数据格式：
  ID:CLOSE
  '''
  def insertMin(self, priceInfo):
    nowtime = time.strftime("%Y-%m-%d %H:%M:00", time.localtime())
    for (k,v) in priceInfo.items():
      stockid = k[2:8]
      if v != None:
        if k[0:2] == 'sz':
          tablename = 'SZ_MIN'
        else:
          tablename = 'SH_MIN'

        #GET MIN AVG PRICE
        min60 = self.getSumByLimit(stockid, 59)
        avg60 = (min60 + float(v))/60
        
        min120 = self.getSumByLimit(stockid, 119)
        avg120 = (min120 + float(v))/120
        
        #min250 = self.getSumByLimit(stockid, 249)
        #avg250 = (min250 + float(v))/250
        avg250 = float(0)
        
        insertStr = "INSERT INTO `%s` \
                    (`ID`, `TIME`,`CLOSE`,`AVG60`,`AVG120`,`AVG250`) \
                    VALUES('%s','%s',%s,%.2f,%.2f,%.2f);" \
                    % (tablename, stockid, nowtime, v, avg60, avg120, avg250)

        self.__cursor.execute(insertStr)
    self.__cursor.execute("COMMIT;")

  '''
  stockdata数据格式：
  ID:CLOSE,HIGH,LOW
  '''
  def insertDay(self, priceInfo):
    nowdate = time.strftime("%Y-%m-%d", time.localtime())
    for (k,v) in priceInfo.items():
      stockid = k[2:8]
      if v != None:
        if k[0:2] == 'sz':
          tablename = 'SZ_DAY'
        else:
          tablename = 'SH_DAY'

        #GET DAY AVG PRICE
        day60 = self.getSumByLimit(stockid, 59, "2")
        avg60 = (day60 + float(v[0]))/60
        
        day120 = self.getSumByLimit(stockid, 119, "2")
        avg120 = (day120 + float(v[0]))/120
        
        #day250 = self.getSumByLimit(stockid, 249, "2")
        #avg250 = (day250 + float(v[0]))/250
        avg250 = float(0)
        
        insertStr = "INSERT INTO `%s` \
                  (`ID`, `CLOSE`,`HIGH`,`LOW`,`DATE`,`AVG60`,`AVG120`,`AVG250`) \
                  VALUES('%s',%s,%s,%s,'%s',%.2f,%.2f,%.2f);" \
                  % (tablename, stockid, v[0], v[1], v[2], nowdate, avg60, avg120, avg250)

        self.__cursor.execute(insertStr)
    self.__cursor.execute("COMMIT;")
      
  '''
  stockdata数据格式：
      Date,Open,High,Low,Close,Volume,Adj Close,60AVG,120AVG,250AVG
  '''
  def initDay(self, stockid, stockdata):
    if len(stockdata) == 0:
      return

    leastDate = stockdata[0][0].replace('/', '-')
    
    #判断是哪个市场的股票
    if stockid[0] == '0':
      tablename = "SZ_DAY"
    else:
      tablename = "SH_DAY"

    if INIT_MODE == '1':
      self.__cursor.execute("DELETE FROM `" + tablename + "` WHERE `ID` = '" + str(stockid) + "';")
      self.__cursor.execute("COMMIT;")
    else:
      delSql = "DELETE FROM `%s` WHERE `ID` = '%s' AND `DATE` <= '%s';" % (tablename, str(stockid), leastDate)
      self.__cursor.execute(delSql)
      self.__cursor.execute("COMMIT;")
    
    for stock in stockdata:
      insertStr = "INSERT INTO `" + tablename + "` \
                  (`ID`, `CLOSE`,`HIGH`,`LOW`,`AVG60`,`AVG120`,`AVG250`,`DATE`) \
                  VALUES('%s',%s,%s,%s,%s,%s,%s,'%s');" \
                  % (stockid, stock[6], stock[2], stock[3], stock[7], stock[8], stock[9], stock[0])
      self.__cursor.execute(insertStr)
    self.__cursor.execute("COMMIT;")
    
    self.__cursor.execute("UPDATE STOCKINFO SET UPDATEDATE = '%s' WHERE ID = '%s';" % (stockdata[0][0],stockid));
    self.__cursor.execute("COMMIT;")
    if DEBUG:
      print "initDay success:" + str(len(stockdata))

  def insertDeal(self, dealInfo):
    for deal in dealInfo:
      insertStr = "INSERT INTO `deal` \
                  (`DATE`, `ID`,`TYPE`,`NUM`,`PRICE`) \
                  VALUES('%s','%s',%s,%s,%s);" \
                  % (deal[0], deal[1], deal[2], deal[3], deal[4])
      print insertStr
      self.__cursor.execute(insertStr)
    self.__cursor.execute("COMMIT;")

  def insertOpp(self, stockdata, mode = 1):
    if mode == 1:
      tablename = "ONE"
    elif mode == 2:
      tablename = "TWO"
    elif mode == 3:
      tablename = "THREE"
    else:
      return
    self.__cursor.execute("DELETE FROM `" + tablename + "`;")
    self.__cursor.execute("COMMIT;")
    
    for stock in stockdata:
      insertStr = "INSERT INTO `" + tablename + "` \
                  (`ID`, `PARAM1`,`PARAM2`,`PARAM3`) \
                  VALUES('%s',%s,%s,%s);" \
                  % (stock[0], stock[1], stock[2], stock[3])
      self.__cursor.execute(insertStr)
    self.__cursor.execute("COMMIT;")

  def initStockById(self, stock):
    stockid,updatedate,name = stock
    
    #获取两年前日期
    #YAHOO获取数据最近两年的数据
    if INIT_MODE == '1':
      stockdata = func.getYahooStockData(stockid)
    else:
      stockdata = func.getFileStockData(stockid)
    
    if stockdata == None:
      print stockid + " has no data!"
      return
    
    stockdata = func.calcStockAvg(stockdata)
    if stockdata == None:
      print stockid + " has no data!"
      return

    print "System is initing " + stockid
      
    #print stockData
    #将数据插入数据库
    self.initDay(stockid, stockdata)
    print stockid + " success!"

  #搜寻60均线机会
  def analyseStockOne(self):
    if DEBUG:
      print "analyseStockOne start"

    #判断是否达到条件1
    sql = "(SELECT TA.ID, MAXPLV, MINPLV, 0 AS PARAM3 FROM ( \
              SELECT ID,MAX((HIGH - AVG60)/AVG60*100) AS MAXPLV \
              FROM SZ_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-60) AND CURDATE() \
              GROUP BY ID \
              ) TA \
              INNER JOIN  \
              ( \
              SELECT ID,MIN((LOW - AVG60)/AVG60*100) AS MINPLV \
              , AVG(AVG60-AVG120) AS AVG60DIFF \
              , AVG(AVG120-AVG250) AS AVG120DIFF \
              FROM SZ_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-5) AND CURDATE() \
              GROUP BY ID \
              ) TB \
              ON TA.ID = TB.ID \
              INNER JOIN  \
              ( \
              SELECT ID,AVG((`CLOSE` - `AVG60`)/`AVG60`)*100 AS AVGPLV \
              FROM SZ_DAY  \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-45) AND ADDDATE(CURDATE(),-15)  \
              GROUP BY ID   \
              ) TC \
              ON TA.ID = TC.ID  \
              WHERE TA.MAXPLV > 15 AND TB.MINPLV < 8 AND TB.MINPLV > 2 AND TB.AVG60DIFF > 0 AND TB.AVG120DIFF > 0 AND TC.AVGPLV > 10) \
              UNION \
              (SELECT TA.ID, MAXPLV, MINPLV, 0 AS PARAM3 FROM ( \
              SELECT ID,MAX((HIGH - AVG60)/AVG60*100) AS MAXPLV \
              FROM SH_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-60) AND CURDATE() \
              GROUP BY ID \
              ) TA \
              INNER JOIN  \
              ( \
              SELECT ID,MIN((LOW - AVG60)/AVG60*100) AS MINPLV \
              , AVG(AVG60-AVG120) AS AVG60DIFF \
              , AVG(AVG120-AVG250) AS AVG120DIFF \
              FROM SH_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-5) AND CURDATE() \
              GROUP BY ID \
              ) TB \
              ON TA.ID = TB.ID \
              INNER JOIN  \
              ( \
              SELECT ID,AVG((`CLOSE` - `AVG60`)/`AVG60`)*100 AS AVGPLV \
              FROM SH_DAY  \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-45) AND ADDDATE(CURDATE(),-15)  \
              GROUP BY ID   \
              ) TC \
              ON TA.ID = TC.ID  \
              WHERE TA.MAXPLV > 15 AND TB.MINPLV < 8 AND TB.MINPLV > 0 AND TB.AVG60DIFF > 0 AND TB.AVG120DIFF > 0 AND TC.AVGPLV > 10)"
    
    result = self.selectAll(sql)
    self.insertOpp(result)

    if DEBUG:
      print "analyseStockOne success"

  #搜寻120均线机会
  def analyseStockTwo(self):
    if DEBUG:
      print "analyseStockTwo start"

    #判断是否达到条件1
    sql = "(SELECT TA.ID, MAXPLV, MINPLV, 0 AS PARAM3 FROM ( \
              SELECT ID,MAX((HIGH - AVG120)/AVG120*100) AS MAXPLV \
              FROM SZ_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-60) AND CURDATE() \
              GROUP BY ID \
              ) TA \
              INNER JOIN  \
              ( \
              SELECT ID,MIN((LOW - AVG120)/AVG120*100) AS MINPLV \
              , AVG(AVG60-AVG120) AS AVG60DIFF \
              , AVG(AVG120-AVG250) AS AVG120DIFF \
              FROM SZ_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-5) AND CURDATE() \
              GROUP BY ID \
              ) TB \
              ON TA.ID = TB.ID \
              INNER JOIN  \
              ( \
              SELECT ID,AVG((`CLOSE` - `AVG120`)/`AVG120`)*100 AS AVGPLV \
              FROM SZ_DAY  \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-45) AND ADDDATE(CURDATE(),-15)  \
              GROUP BY ID   \
              ) TC \
              ON TA.ID = TC.ID  \
              WHERE TA.MAXPLV > 15 AND TB.MINPLV < 8 AND TB.MINPLV > 2 AND TB.AVG60DIFF > 0 AND TB.AVG120DIFF > 0 AND TC.AVGPLV > 10) \
              UNION \
              (SELECT TA.ID, MAXPLV, MINPLV, 0 AS PARAM3 FROM ( \
              SELECT ID,MAX((HIGH - AVG120)/AVG120*100) AS MAXPLV \
              FROM SH_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-60) AND CURDATE() \
              GROUP BY ID \
              ) TA \
              INNER JOIN  \
              ( \
              SELECT ID,MIN((LOW - AVG120)/AVG120*100) AS MINPLV \
              , AVG(AVG60-AVG120) AS AVG60DIFF \
              , AVG(AVG120-AVG250) AS AVG120DIFF \
              FROM SH_DAY \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-5) AND CURDATE() \
              GROUP BY ID \
              ) TB \
              ON TA.ID = TB.ID \
              INNER JOIN  \
              ( \
              SELECT ID,AVG((`CLOSE` - `AVG120`)/`AVG120`)*100 AS AVGPLV \
              FROM SH_DAY  \
              WHERE `DATE` BETWEEN ADDDATE(CURDATE(),-45) AND ADDDATE(CURDATE(),-15)  \
              GROUP BY ID   \
              ) TC \
              ON TA.ID = TC.ID  \
              WHERE TA.MAXPLV > 15 AND TB.MINPLV < 8 AND TB.MINPLV > 0 AND TB.AVG60DIFF > 0 AND TB.AVG120DIFF > 0 AND TC.AVGPLV > 10 \
              AND NOT EXISTS (SELECT * FROM ONE WHERE ID = TA.ID))"
    
    result = self.selectAll(sql)
    self.insertOpp(result, 2)

    if DEBUG:
      print "analyseStockTwo success"

  #获取最新的均价信息
  def getMonitAvgInfo(self):
    sql1 = " (SELECT MIN_T.ID AS ID, MIN_AVG, DAY_AVG \
              FROM  \
              ( \
                SELECT ID AS ID, AVG60 AS MIN_AVG  \
                FROM sz_min \
                WHERE time = (SELECT MAX(time) FROM sz_min) \
                UNION  \
                SELECT ID AS ID, AVG60 AS MIN_AVG60  \
                FROM sh_min \
                WHERE time = (SELECT MAX(time) FROM sh_min) \
              ) MIN_T \
              INNER JOIN  \
              ( \
                SELECT MAIN.ID AS ID, MAIN.AVG60 AS DAY_AVG \
                FROM sz_day MAIN  \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sz_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
                UNION  \
                SELECT MAIN.ID AS ID, MAIN.AVG60 AS DAY_AVG \
                FROM sh_day MAIN \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sh_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
              ) DAY_T \
              ON MIN_T.ID = DAY_T.ID \
              WHERE EXISTS (SELECT * FROM V_OPP WHERE ID = MIN_T.ID AND V_OPP.TYPE = 1)) "

    sql2 = " (SELECT MIN_T.ID AS ID, MIN_AVG, DAY_AVG \
              FROM  \
              ( \
                SELECT ID AS ID, AVG60 AS MIN_AVG \
                FROM sz_min \
                WHERE time = (SELECT MAX(time) FROM sz_min) \
                UNION  \
                SELECT ID AS ID, AVG60 AS MIN_AVG60  \
                FROM sh_min \
                WHERE time = (SELECT MAX(time) FROM sh_min) \
              ) MIN_T \
              INNER JOIN  \
              ( \
                SELECT MAIN.ID AS ID, MAIN.AVG120 AS DAY_AVG \
                FROM sz_day MAIN  \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sz_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
                UNION  \
                SELECT MAIN.ID AS ID, MAIN.AVG120 AS DAY_AVG120 \
                FROM sh_day MAIN \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sh_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
              ) DAY_T \
              ON MIN_T.ID = DAY_T.ID \
              WHERE EXISTS (SELECT * FROM V_OPP WHERE ID = MIN_T.ID AND V_OPP.TYPE = 2)); "
    
    sql = sql1 + " UNION " + sql2
    result = self.selectAll(sql)
    return result

  #获取特定股票的最新的均价信息
  def getAvgInfoById(self, stockid, mode):
    #基于60日线的机会
    if mode == "1":
      sql  = " SELECT MIN_T.ID AS ID, MIN_AVG, DAY_AVG \
              FROM  \
              ( \
                SELECT ID AS ID, AVG60 AS MIN_AVG  \
                FROM sz_min \
                WHERE time = (SELECT MAX(time) FROM sz_min) \
                UNION  \
                SELECT ID AS ID, AVG60 AS MIN_AVG60  \
                FROM sh_min \
                WHERE time = (SELECT MAX(time) FROM sh_min) \
              ) MIN_T \
              INNER JOIN  \
              ( \
                SELECT MAIN.ID AS ID, MAIN.AVG60 AS DAY_AVG \
                FROM sz_day MAIN  \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sz_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
                UNION  \
                SELECT MAIN.ID AS ID, MAIN.AVG60 AS DAY_AVG \
                FROM sh_day MAIN \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sh_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
              ) DAY_T \
              ON MIN_T.ID = DAY_T.ID \
              WHERE MIN_T.ID = '" + stockid + "';"

    #基于120日线的机会
    if mode == "2":
      sql  = " SELECT MIN_T.ID AS ID, MIN_AVG, DAY_AVG \
              FROM  \
              ( \
                SELECT ID AS ID, AVG60 AS MIN_AVG  \
                FROM sz_min \
                WHERE time = (SELECT MAX(time) FROM sz_min) \
                UNION  \
                SELECT ID AS ID, AVG60 AS MIN_AVG60  \
                FROM sh_min \
                WHERE time = (SELECT MAX(time) FROM sh_min) \
              ) MIN_T \
              INNER JOIN  \
              ( \
                SELECT MAIN.ID AS ID, MAIN.AVG120 AS DAY_AVG \
                FROM sz_day MAIN  \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sz_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
                UNION  \
                SELECT MAIN.ID AS ID, MAIN.AVG120 AS DAY_AVG \
                FROM sh_day MAIN \
                INNER JOIN  \
                ( \
                  SELECT ID AS ID ,MAX(DATE) AS MAX_DATE \
                  FROM sh_day \
                  GROUP BY ID \
                ) TA \
                ON MAIN.ID = TA.ID AND MAIN.DATE = TA.MAX_DATE \
              ) DAY_T \
              ON MIN_T.ID = DAY_T.ID \
              WHERE MIN_T.ID = '" + stockid + "';"

    result = self.selectOne(sql)
    return result

  '''
  处理交易记录数据
  将已完结的交易数据存入交易履历表
  '''
  def initDealData(self):
    #获取当前交易统计数据
    sqlDeal = "SELECT BUY.ID, BUY_SUM-SELL_SUM \
                FROM \
                ( \
                SELECT ID, SUM(NUM) AS BUY_SUM \
                FROM DEAL \
                WHERE TYPE = '1' \
                GROUP BY ID \
                ) BUY \
                INNER JOIN \
                ( \
                SELECT ID, SUM(NUM) AS SELL_SUM \
                FROM DEAL \
                WHERE TYPE = '2' \
                GROUP BY ID \
                ) SELL ON BUY.ID = SELL.ID "
    dealInfo = self.selectAll(sqlDeal)
    for deal in dealInfo:
      if float(deal[1]) == 0:
        #交易完结，进入交易履历表
        sqlInsert = "INSERT INTO dealhistory \
                    (DATE, ID, TYPE, NUM, PRICE) \
                    SELECT DATE, ID, TYPE, NUM, PRICE FROM DEAL \
                    WHERE ID = '" + deal[0] + "'" 
        self.__cursor.execute(sqlInsert)
        self.__cursor.execute("COMMIT;")
        #删除交易完结数据
        sqlDelete = "DELETE FROM deal WHERE ID = '" + deal[0] + "'"
        self.__cursor.execute(sqlDelete)
        self.__cursor.execute("COMMIT;")
    
  '''
  获取当前持有股及其基准价
  '''
  def getDealMonitInfo(self):
    sqlGet = "SELECT ID, MAX(PRICE) AS PRICE FROM DEAL GROUP BY ID"
    return self.selectAll(sqlGet)

  '''
  获取最近的N条记录的收盘价总和
  mode:1-min;2-day
  '''
  def getSumByLimit(self, stockid, limit, mode = "1"):
    #GET TABLE BY STOCKID AND MODE
    if mode == "1":
      order = "TIME"
      if stockid[0] == "0":
        table = "SZ_MIN"
      else:
        table = "SH_MIN"
    else:
      order = "DATE"
      if stockid[0] == "0":
        table = "SZ_DAY"
      else:
        table = "SH_DAY"
    
    sql = "SELECT SUM(T.CLOSE) \
            FROM  \
            ( \
                    SELECT ID, CLOSE \
                    FROM `%s`  \
                    WHERE ID = %s \
                    ORDER BY %s DESC \
                    LIMIT %s \
            ) T" % (table, stockid, order, limit)
    result = self.selectOne(sql)
    return float(result[0])
