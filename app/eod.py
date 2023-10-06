import pandas as pd
import csv
import pymongo
cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
all_sym = ["NIFTY","BANKNIFTY"]
alert_check = []
db = cl.zerodha_index
def seperate(token):
    global price_tokens
    global all_tokens
    global all_inst
    monthly_list = []
    weekly_list = []
    token = token.upper()
    lst =['MONTHLY',"WEEKLY"]
    for l in lst:
     table = db[token+l]
     results = table.find()
     for result in results:
       if result['oi'] != -1:
        new = { "$set" : { "poi": result['oi'],"oi":-1}}
        table.update_one({"_id": result["_id"]},new)




for sym in all_sym:
 print(sym)
 seperate(sym)

table = db['priceList']
results = table.find()
for result in results:
   if result['CMP'] != 0:
        new = { "$set" : { "CLOSE": result['CMP'],"CMP":0}}
        table.update_one({"_id": result["_id"]},new)




db['alerts'].drop()

altable = db['alertCheck']
table  = altable.find()
for tab in table:
   s = (list(tab.keys()))
   #print(s[1])
   if tab[s[1]] == 1:
        new = { "$set" : { s[1]:0}}
        altable.update_one({"_id": tab["_id"]},new)

