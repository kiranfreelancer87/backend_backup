import pymongo
import datetime
from dateutil.tz import gettz
#dtobj = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
#current = dtobj.time()
#print(dtobj.strftime("%d %b %y, %H:%M:%S"))
#start = datetime.time(1,15,00)
#end = datetime.time(15,30,00)
#if ( start <= current <= end):
# print("111")
#with open('token.txt',"r") as file:
#	first_line = file.readline()
#print((first_line).strip())
cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
db = cl.zerodha
altable = db['creds']
table  = altable.find()
#table = db['priceList'].find()
for tab in table:
    print(tab)
#print(cl.list_database_names())
#from al import send_alert
#import asyncio
#asyncio.run(send_alert({'sda':1234,"sadasd":{"112":11,"sadad":"asda"}}))
#tok_table = db['creds']
#tok_result = list(tok_table.find({'id':"access_token" }))
#tok = tok_result[0]['value']
#print(tok)
