from kiteconnect import KiteTicker
from kiteconnect import KiteConnect
from db3 import cash_price_update, get_token
import pymongo
import csv
import os

import asyncio
import logging
logging.getLogger('asyncio').setLevel(logging.WARNING)
all_tokens =[]


cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
db = cl.zerodha_index
table  = db['cashPriceList'].find()
for tab in table:
    all_tokens.append(tab['id'])

print(all_tokens)

logging.basicConfig(level=logging.DEBUG)
api_key = "w60j5yagqsbomli1"
access_token = get_token()
print(access_token)

###api_key = "tfgh4ol377nnenrr"
###access_token  = "SQF6tiB1IEl3O1C3yu1LYwAfrjzkkZ62"

kws = KiteTicker(api_key,access_token)


def on_ticks(ws, ticks):
    for tick in ticks:
            try:
                print(tick['instrument_token'],tick['last_price'])
                asyncio.run(cash_price_update(tick['instrument_token'], tick['last_price']))
            except Exception as e:
                print("error",e)

    #logging.debug("Ticks: {}".format(ticks))

def on_connect(ws, response):
   
    
    print("start")
    ws.subscribe(all_tokens)
    ws.set_mode(ws.MODE_FULL, all_tokens)
    

def on_close(ws, code, reason):
   
    print(reason)
    #ws.stop()

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

kws.connect(threaded=False)
