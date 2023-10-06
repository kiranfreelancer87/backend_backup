from kiteconnect import KiteTicker
from kiteconnect import KiteConnect
from db3 import price_update, get_token, update_strong
import pymongo
import csv
import os
import threading
import asyncio
import logging
import time
logging.getLogger('asyncio').setLevel(logging.WARNING)


class RepeatedTimer(object):

    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


all_tokens =[]


cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
db = cl.zerodha_index
table  = db['priceList'].find()
for tab in table:
    all_tokens.append(tab['id'])

print(all_tokens)

logging.basicConfig(level=logging.DEBUG)
api_key = "w60j5yagqsbomli1"
#api_key = "tfgh4ol377nnenrr"
access_token = get_token()
print(access_token)

###api_key = "tfgh4ol377nnenrr"
###access_token  = "SQF6tiB1IEl3O1C3yu1LYwAfrjzkkZ62"

#with open('token.txt',"r") as file:
 #       first_line = file.readline()
#access_token = first_line.strip()

#access_token  = "Hud7WEJ1JUOsjW2HHM076F2ax0kMquM7 "
kws = KiteTicker(api_key,access_token)
token =[31064834,31065090,31065346,31065602]

#def candle():
 #  print("123")
  # asyncio.run(update_strong())

#ema1 = RepeatedTimer(45, candle)

        
def on_ticks(ws, ticks):
   
    for tick in ticks:
        
        if tick and 'oi' in tick:
            try:
                #asyncio.run(oi_update(tick['instrument_token'], tick['oi']))
                print(tick['last_price'])
                asyncio.run(price_update(tick['instrument_token'], tick['last_price']))
                #oi_update(tick['instrument_token'], tick['oi'])
            except Exception as e:
                print("error",e)

    #logging.debug("Ticks: {}".format(ticks))

def on_connect(ws, response):
   
    
    print("start")
    ws.subscribe(all_tokens)
    ws.set_mode(ws.MODE_FULL, all_tokens)
    

def on_close(ws, code, reason):
   
    print(reason)
    # Reconnection will not happen after executing `ws.stop()`
    #ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect(threaded=False)
