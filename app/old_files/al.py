import json
import pymongo
import requests
import datetime
from copy import deepcopy
from dateutil.tz import gettz

cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
db = cl.zerodha


async def add_alert(alert):
    table = db['alerts']
    in_table = table.insert_one(alert)
    return



async def send_alert(alert_info):
    print("============================NEW ALERT================================")
    print(alert_info)
    url = 'http://remote-vpn.com/alert'
    myobj = alert_info
    #x = requests.post(url, json = myobj)
    #print(x.text)
    await add_alert(alert_info)
   # try:
    #   with open("alerts.txt","a") as file:
     #      file.write(str(alert_info)+"\n")
   # except Exception as e:
    #   print(e)


