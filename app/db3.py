import json
import telegram
import pymongo
import requests
import datetime
from copy import deepcopy
from dateutil.tz import gettz

cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
db = cl.zerodha_index

def get_token():
    db = cl.zerodha
    tok_table = db['creds']
    tok_result = list(tok_table.find({'id':"access_token" }))
    access_token = tok_result[0]['value']
    return access_token

async def time_check():
    dtobj = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    current = dtobj.time()
    start = datetime.time(9,15,00)
    end = datetime.time(15,30,00)
    #return "1"
    if (start <= current <= end):
      return "1"
    elif (end <= current):
      return "2"
    elif (current <= start):
      return "3"

async def price_update(token,price):
    token = int(token)
    price = float(price)
    table = db['priceList']
    tc = await time_check()
    if tc == "1":
     in_table = table.update_one({'id':token}, {'$set':{"CMP": price}})
     ck_table = table.find({'id': int(token)})
     asset = ck_table[0]['name']
     expiry = ck_table[0]['expiry']
     cp_result = db['cashPriceList'].find_one({"name":asset})
     cash_price = cp_result['CMP']
     #print(asset,price,expiry)
     result = await check_highest(asset, price, expiry,cash_price)
    return


async def cash_price_update(token,price):
    token = int(token)
    price = float(price)
    table = db['cashPriceList']
    tc = await time_check()
    #print(tc)
    if tc == "1":
     in_table = table.update_one({'id':token}, {'$set':{"CMP": price}})
    return

async def update_strong():
   tc = await time_check()
   if tc == "1":
    table = db['priceList']
    ck_table = list(table.find({}))
    for res in ck_table:
     price = res['CMP']
     asset = res['name']
     expiry = res['expiry']
     result = await check_highest(asset, price, expiry)

async def oi_update_three(token,oi,exch_time):
    ts = await time_check()
    if ts == "1":
      token = int(token)
      oi = int(oi)
      table  = db['allList']
      get_table = table.find({'id': int(token)})
      table_name = get_table[0]['table']
      #print(token, oi, table_name)
      inst_table = db[table_name]
      in_table = inst_table.update_one({'id':token}, {'$set':{"oi": oi,}})
      if exch_time.second == 0:
          side_res = inst_table.find_one({'id':token})
          side = side_res['side']
          oi_table = db[table_name+"_OI"]
          noi_table =  db[table_name+"_OI_"+side]
          in_oi_table = oi_table.update_one({'t': exch_time}, {'$inc': {side: int(oi)}},upsert=True)
          nin_oi_table = noi_table.update_one({"t":exch_time},{"$set":{str(token):oi}},upsert=True)
      #asset = get_table[0]['asset']
      #lp_table = db['priceList']
      #lp_result = list(lp_table.find({'name': asset.upper()}))
      #expiry = get_table[0]['expiry']
      #lp = lp_result[0]['CMP']
      return
      #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
      #print(asset.upper(),lp_result)
      #result = await check_highest(asset, lp, expiry)


async def get_details(asset):
    data = {}
    data['weekly'] = {}
    asset = asset.upper()
    table_weekly = db[asset+"WEEKLY"]
    week_data =list(table_weekly.find({}))

    #print(2.2)
    for t_data in week_data:
        if t_data['expiry'] in data['weekly']:
            if t_data['strike'] in data['weekly'][t_data['expiry']]:
                data['weekly'][t_data['expiry']][t_data['strike']][t_data['side']] = {"oi":t_data['oi'],"poi":t_data['poi']}
            else:
                data['weekly'][t_data['expiry']][t_data['strike']] = {}
                data['weekly'][t_data['expiry']][t_data['strike']][t_data['side']] = {"oi":t_data['oi'],"poi":t_data['poi']}
        else:
            data['weekly'][t_data['expiry']] ={}
            data['weekly'][t_data['expiry']][t_data['strike']] = {} 
            data['weekly'][t_data['expiry']][t_data['strike']][t_data['side']] = {"oi":t_data['oi'],"poi":t_data['poi']}
    #print(data)
    return data

async def add_alert(alert):
    table = db['alerts3']
    in_table = table.insert_one(alert)
    return

async def telegram_alert(raw):
   try:
      msg_text = "Negative Threshold : "
      if str(raw['values']['highest_side']) == "PE":
         msg_text = "Positive Threshold : "
      newline = "\n"
      alert = "3. Time : "+str(raw['at_time'])+newline+ \
        "Name : "+raw['name']+newline + \
        msg_text + str(raw['values']['strike'])+newline
        #"Expiry : " + raw['expiry']+newline+ \
        #"Number: "+ str(raw['number'])+newline+ \
        #"Oi Diff : " +str(raw['ratio'])+" times"+newline+ \
        #"Oi VALUES"+newline+ \
        #"High Side : "+ str(raw['values']['highest_side'])+", OI : "+str(raw['values']['highest_value'])+newline+ \
        #"Low Side  : "+ str(raw['values']['other_side'])+", OI : "+str(raw['values']['other_value'])+newline+ \
        #"CMP : "+ str(raw['values']['CMP'])

      bot_token = '5913260956:AAFug7aSD5a_waFDDqXXZxHedxxRKvzWXwk'
      chat_id = "-1001799713389"
      bot = telegram.Bot(token=bot_token)
      bot.send_message(chat_id=chat_id, text=alert)
   except Exception as e:
      with open("tg_alert.txt","a") as file:
       file.write(str(e)+"\n")

      return

async def send_alert(alert_info):
    print("============================NEW ALERT================================")
    print(alert_info)
    url = 'https://lokmaarenko.com/alert3'
    myobj = alert_info
    x = requests.post(url, json = myobj)
    print(x.text)
    try:
       with open("/home/app/alerts3.txt","a") as file:
           file.write(str(alert_info)+"\n")
    except Exception as e:
       print(e)
    s = await add_alert(alert_info)
    tg = await telegram_alert(alert_info)


async def strikes_seperate(lst, ref):
    lst.sort() 
    closest_greater = []
    closest_less = []
    for i in range(len(lst)):
        if lst[i] > ref:
            closest_greater.append(lst[i])
        elif lst[i] < ref:
            closest_less.append(lst[i])
    closest_less.reverse()
    return closest_greater, closest_less

async def check_strong(x):
   if x >= 1.6 and x < 1.8:
     return 70
   elif x >= 1.8 and x < 2.0:
     return 80
   elif x >= 2.0 and x < 2.5:
     return 90
   elif x >= 2.5:
     return 95

async def round_closest_strike(number,ref):
    return round(number / ref) * ref

async def check_highest(asset,lp,expiry,cash_price):
    #print(asset)
    #if asset == "BANKNIFTY":
     # return 0
    result = {"above":[],"below":[]}
    asset = asset.upper()
    time_frame = "weekly"
    sos = await get_details(asset)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print(asset)
    #print(sos)
    strikes_dict = list(sos["weekly"][expiry].keys())
    strike_above, strike_below = await strikes_seperate(strikes_dict, lp)

    strike_diff  = abs(strike_above[1] - strike_above[0])
    cp_fut_diff =  cash_price - lp
    print("------------------",cp_fut_diff,strike_diff)
    #print(strike_above)
    #print("111111111111111111111111111111111111111111111111111111111111111111111")
    #print(strike_below)
    
    print(1)
    for value in strike_above:
        #print(1.1,value)
        try:
         ce = int(sos[time_frame.lower()][expiry][value]['CE']['oi']) + 1
        except:
         ce = 1
        try:
          pce =  int(sos[time_frame.lower()][expiry][value]['CE']['poi']) + 1
        except:
          pce = 1
        try:
           pe = int(sos[time_frame.lower()][expiry][value]['PE']['oi']) + 1
        except:
          pe = 1
        try:
           ppe = int(sos[time_frame.lower()][expiry][value]['PE']['poi']) + 1
        except:
           ppe = 1
        chg_ce = int(ce)- int(pce)
        chg_pe = int(pe) - int(ppe)
        #print(pe,ce,chg_pe,chg_ce)
        if ce >= 1.6*pe and ce > 0 and pe > 0 and ppe > 0 and pce > 0 and chg_ce >= 1.6*chg_pe and len(result["above"]) < 5:
          #print("high",value,  pe,ce,chg_pe,chg_ce)
          oi_diff = ce/pe
          chg_diff = chg_ce/chg_pe
          oi_strong = await check_strong(oi_diff)
          chg_strong = await check_strong(chg_diff)
          result["above"].append([value,oi_strong,chg_strong])

    for value in strike_below:
        #print(2.1,value)
        try:
           ce = int(sos[time_frame.lower()][expiry][value]['CE']['oi']) +1
        except:
           ce =1
        try:
            pce =  int(sos[time_frame.lower()][expiry][value]['CE']['poi'])+ 1
        except:
            pce = 1
        try:
           pe = int(sos[time_frame.lower()][expiry][value]['PE']['oi']) + 1
        except:
          pe = 1
        try: 
          ppe = int(sos[time_frame.lower()][expiry][value]['PE']['poi']) + 1
        except:
          ppe = 1
        chg_ce = int(ce)- int(pce)
        chg_pe = int(pe) - int(ppe)
        #print(pe,ce,chg_pe,chg_ce)
        if pe >= 1.6*ce and ce > 0 and pe > 0 and ppe > 0 and pce > 0 and chg_pe >= 1.6*chg_ce and len(result["below"]) < 5:
           #print("low",value, pe,ce,chg_pe,chg_ce)
           oi_diff = pe/ce
           chg_diff = chg_pe/chg_ce
           oi_strong = await check_strong(oi_diff)
           chg_strong = await check_strong(chg_diff)
           result["below"].append([value,oi_strong,chg_strong])
    
    one = {"a":{},"b":{}}
    two = {"a":{},"b":{}}
    three ={"a":{},"b":{}}
    four = {"a":{},"b":{}}
    five = {"a":{},"b":{}}
    #print(result)
    #print(2)
    resx = 0
    for x in result['above']:
      resx += 1
      #fut_strike_diff = x[0] - lp
      #final_strike = await round_closest_strike((cash_price + fut_strike_diff),strike_diff)
      if resx == 1:
      	one['a'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 2:
        two['a'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 3:
        three['a'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 4:
        four['a'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 5:
        five['a'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
    one['a']['name'] = "resistance_one"
    two['a']['name'] = "resistance_two"
    three['a']['name'] = "resistance_three"
    four['a']['name'] = "resistance_four"
    five['a']['name'] = "resistance_five"
    resx = 0
    for x in result['below']:
      resx += 1
      #fut_strike_diff = lp - x[0]
      #final_strike = await round_closest_strike((cash_price - fut_strike_diff),strike_diff)
      if resx == 1:
        one['b'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 2:
        two['b'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 3:
        three['b'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 4:
        four['b'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}
      elif resx == 5:
        five['b'] = {'strike':x[0],'oi':x[1],'oichg':x[2]}

    one['b']['name'] = "support_one"
    two['b']['name'] = "support_two"
    three['b']['name'] = "support_three"
    four['b']['name'] = "support_four"
    five['b']['name']= "support_five"
    #print(one,two,three,four)
    #print(3)

    table = db[asset.lower()+"_strong"]
    table.drop()
    r1 = table.update_one({'name': "resistance_one"}, {"$set": one["a"]}, upsert=True)
    r2 = table.update_one({'name': "resistance_two"}, {"$set": two["a"]}, upsert=True)
    r3 = table.update_one({'name': "resistance_three"}, {"$set":three["a"]}, upsert=True)
    r4 = table.update_one({'name': "resistance_four"}, {"$set": four["a"]}, upsert=True)
    r5 = table.update_one({'name': "resistance_five"}, {"$set": five["a"]}, upsert=True)
    #print(r1.upserted_id,r2.upserted_id,r3.upserted_id,r4.upserted_id)
    s1 = table.update_one({'name': "support_one"}, {"$set": one["b"]}, upsert=True)
    s2 = table.update_one({'name': "support_two"}, {"$set": two["b"]}, upsert=True)
    s3 = table.update_one({'name': "support_three"}, {"$set": three["b"]}, upsert=True)
    s4 = table.update_one({'name': "support_four"}, {"$set": four["b"]}, upsert=True)
    s5 = table.update_one({'name': "support_five"}, {"$set": five["b"]}, upsert=True)
    print(4)
    return 0
    try:
     table_per = db[asset.lower()+"all_up"]
     table.update_one({"strike":one["a"]["strike"]}, {"$set": one["a"]}, upsert=True)
     table.update_one({"strike":two["a"]["strike"]}, {"$set": two["a"]}, upsert=True)
     table.update_one({"strike":three["a"]["strike"]}, {"$set":three["a"]}, upsert=True)
     table.update_one({"strike":four["a"]["strike"]}, {"$set": four["a"]}, upsert=True)

     table_per = db[asset.lower()+"all_down"]
     table.update_one({"strike":one["b"]["strike"]}, {"$set": one["b"]}, upsert=True)
     table.update_one({"strike":two["b"]["strike"]}, {"$set": two["b"]}, upsert=True)
     table.update_one({"strike":three["b"]["strike"]}, {"$set":three["b"]}, upsert=True)
     table.update_one({"strike":four["b"]["strike"]}, {"$set": four["b"]}, upsert=True)
    except Exception as e:
     print(str(e))
    return 0

