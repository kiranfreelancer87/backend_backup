import pandas as pd
import json
import pymongo
import requests
import datetime
from copy import deepcopy
from dateutil.tz import gettz



cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/")
db = cl.zerodha
df = pd.read_csv('csv/fo.csv')
all_sym = df["SYMBOL \n"].tolist()
alert_check = []
db = cl.zerodha

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
     print({"call_prev":tcpoi,"put_prev":tppoi,"call_cur": tcoi,"curr_put":tpoi})
     diff  = tpoi - tcoi
     total_ce_change = tcoi - tcpoi
     total_pe_change = tpoi - tppoi
     total_oi_change  = total_pe_change - total_ce_change
     a = total_pe_change - total_ce_change
     b = total_ce_change + total_pe_change
     try:
       c = (a/b)*100
       #table_new  = db['new']
       print({"name":token,"total_ce_oi":tcoi,"total_pe_oi":tpoi,"diff":diff,"total_pe_change":total_pe_change,"total_ce_change":total_ce_change,"change_diff":total_oi_change, "percent_change":c})
       # new = { "$set" : { "poi": result['oi'],"oi":-1}}
        #table.update_one({"_id": result["_id"]},new)
     except Exception as e:
         print(str(e))



#for sym in all_sym:
 #print(sym)
seperate("BPCL")
