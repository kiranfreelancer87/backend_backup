import pandas as pd
import json
import pymongo
import requests
import datetime
from copy import deepcopy
from dateutil.tz import gettz

while True:
   # break
    dtobj = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    a = dtobj.time()
    b = datetime.time(9,20,5)
    if a > b:
      break


cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/")
db = cl.zerodha
df = pd.read_csv('/home/app/csv/fo.csv')
all_sym = df["SYMBOL \n"].tolist()
alert_check = []
db = cl.zerodha
db['new'].drop()
def seperate(token):
    tcpoi = 0
    tppoi = 0
    tcoi = 0
    tpoi = 0
    monthly_list = []
    weekly_list = []
    token = token.upper()
    lst =['MONTHLY']
    for l in lst:
     table = db[token+l]
     results = table.find()
     for result in results:
        if result['side'] == "CE":
          tcpoi = tcpoi + int(result['poi'])
          tcoi  = tcoi + int(result['oi'])
        else:
          tppoi = tppoi + int(result['poi'])
          tpoi  = tpoi+ int(result['oi'])
     diff  = tpoi - tcoi
     total_ce_change = tcoi - tcpoi
     total_pe_change = tpoi - tppoi
     total_oi_change  = total_pe_change - total_ce_change
     total_oi_change_ce = total_ce_change - total_pe_change
     a = total_pe_change - total_ce_change
     b = total_ce_change + total_pe_change
     try:
       c = (a/b)*100
       table_new  = db['new']
       table_new.insert_one({"name":token,"total_ce_oi":tcoi,"total_pe_oi":tpoi,"diff":diff,"total_pe_change":int(total_pe_change),"total_ce_change":int(total_ce_change),"change_diff_ce":int(total_oi_change_ce),"change_diff":int(total_oi_change), "percent_change":c})
       # new = { "$set" : { "poi": result['oi'],"oi":-1}}
        #table.update_one({"_id": result["_id"]},new)
     except Exception as e:
         print(str(e))



for sym in all_sym:
 print(sym)
 seperate(sym)
