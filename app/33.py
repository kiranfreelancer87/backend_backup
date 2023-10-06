from kiteconnect import KiteTicker
from kiteconnect import KiteConnect
from db3 import get_token,oi_update_three

import pymongo
import csv
import os
import sys
try: 
 x = sys.argv[1]
 x = x.upper()
except:
 pass
import asyncio
import logging
logging.getLogger('asyncio').setLevel(logging.WARNING)
all_tokens =[]

#with open('token.txt',"r") as file:
 #       first_line = file.readline()
#access_token = first_line.strip()

access_token = get_token()
print(access_token)

with open ("/home/app/csv/"+x+".csv","r") as f:
    reader = csv.reader(f) 
    for row in reader:
        all_tokens.append(int(row[0]))
    

import logging
logging.basicConfig(level=logging.DEBUG)
##original api
api_key = "w60j5yagqsbomli1"
#api_key = "tfgh4ol377nnenrr"
#access_token  = "Hud7WEJ1JUOsjW2HHM076F2ax0kMquM7 "
kws = KiteTicker(api_key,access_token)
token =[19995906,19996162,27196674,27196930,27197186,27197442,27196162,27196418,26963714,26963970]
    
        
def on_ticks(ws, ticks):
    # Callback to receive ticks.
    #print(ticks[0]['oi'],ticks[0]['instrument_token'],ticks[0]['ohlc']['close'])
    for tick in ticks:
        print(tick)
        #print(tick['oi'])
        #print(tick['instrument_token'], tick['oi'], type(tick['instrument_token']), type(tick['oi']))
        if tick and 'oi' in tick:
            try:
                pass
                #if tick['exchange_timestamp'].second == 0:
                 #print (tick['exchange_timestamp'],tick['instrument_token'], tick['oi'])
                #asyncio.run(oi_update_three(tick['instrument_token'], tick['oi'],tick['exchange_timestamp']))
            except Exception as e:
                print("error",e)

    #logging.debug("Ticks: {}".format(ticks))
#all_tokens = [33912066,33912322]
def on_connect(ws, response):
   
    #ws.subscribe(token)
    #ws.set_mode(ws.MODE_FULL, token)
    print("start")
    ws.subscribe(all_tokens)
    ws.set_mode(ws.MODE_FULL, all_tokens)
    #ws.subscribe(all_tokens[x:y])
    #ws.set_mode(ws.MODE_FULL, all_tokens[x:y])
    

def on_close(ws, code, reason):
    # On connection close stop the main loop
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
