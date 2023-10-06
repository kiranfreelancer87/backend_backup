import json
import telegram
import pymongo
import requests
import datetime
from copy import deepcopy
from dateutil.tz import gettz

cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
db = cl.zerodha

def get_token():
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
    #print(tc)
    if tc == "1":
     #print("123")
     in_table = table.update_one({'id':token}, {'$set':{"CMP": price}})
    return

async def cash_price_update(token,price):
    token = int(token)
    price = float(price)
    table = db['cashPriceList']
    tc = await time_check()
    #print(tc)
    if tc == "1":
     #print("123")
     in_table = table.update_one({'id':token}, {'$set':{"CMP": price}})
    return

async def oi_update_two(token,oi):
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
      asset = get_table[0]['asset']
      time_frame = get_table[0]['frame']
      expiry = get_table[0]['expiry']
      lcp_table = db['cashPriceList']
      lcp_result = list(lcp_table.find({'name': asset.upper()}))
      print(lcp_result)
      if len(lcp_result) > 0:
        lcp = lcp_result[0]['CMP']
      else:
        lcp = 0
      lp_table = db['priceList']
      lp_result = list(lp_table.find({'name': asset.upper()}))
      print(asset.upper(),lp_result)
      lp = lp_result[0]['CMP']
      pclose = lp_result[0]['CLOSE']
      print("+++++++++++++++++++++++++++++++++++++++++++++++++")
      result = await check_highest(asset,time_frame,expiry, lp, pclose,lcp)
    #elif ts == 2:
     # oi_update()


async def get_details(asset):
    data = {}
    data['monthly'] ={}
    data['weekly'] = {}
    
    asset = asset.upper()
    table_weekly = db[asset+"WEEKLY"]
    table_monthly = db[asset+"MONTHLY"]
    
    month_data =list(table_monthly.find({}))
    week_data = list(table_weekly.find({}))
    #print(month_data)

    
    for t_data in month_data:
        #print(t_data)
        #print(data['monthly'])
        if t_data['expiry'] in data['monthly']: 
            #print(data['monthly'][t_data['expiry'])
            if t_data['strike'] in data['monthly'][t_data['expiry']]:
                data['monthly'][t_data['expiry']][t_data['strike']][t_data['side']] =  {"oi":t_data['oi'],"poi":t_data['poi']}
            else:
                data['monthly'][t_data['expiry']][t_data['strike']] = {}
                data['monthly'][t_data['expiry']][t_data['strike']][t_data['side']] = {"oi":t_data['oi'],"poi":t_data['poi']}
        else:
            data['monthly'][t_data['expiry']] ={}
            data['monthly'][t_data['expiry']][t_data['strike']] = {} 
            data['monthly'][t_data['expiry']][t_data['strike']][t_data['side']] = {"oi":t_data['oi'],"poi":t_data['poi']}
            
    for t_data in week_data:        
        if t_data['expiry'] in data['weekly']: 
            #print(data['monthly'][t_data['expiry'])
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
    table = db['alerts2']
    in_table = table.insert_one(alert)
    return

async def telegram_alert(raw):
   try:
      msg_text = "Negative Threshold : "
      if str(raw['values']['highest_side']) == "PE":
         msg_text = "Positive Threshold : "
      newline = "\n"
      alert = "2. Time : "+str(raw['at_time'])+newline+ \
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
    url = 'https://lokmaarenko.com/alert2'
    myobj = alert_info
    x = requests.post(url, json = myobj)
    print(x.text)
    try:
       with open("/home/app/alerts2.txt","a") as file:
           file.write(str(alert_info)+"\n")
    except Exception as e:
       print(e)
    s = await add_alert(alert_info)
    tg = await telegram_alert(alert_info)


async def check_highest(asset,time_frame,expiry,lp, pclose,lcp):
    
    #print("=========================================")
    asset = asset.upper()
    table = db['alertCheck2']
    get_table = list(table.find({asset: 0}))
    
    if len(get_table) < 1:
        print(get_table)
        return
    sos = await get_details(asset.upper())
    #for keys in sos['monthly']:
     #   print(keys)
    highest = {"number":"1st","CE":{},"PE":{}}
    second_high  = {"number":"2nd","CE":{},"PE":{}}
    third_high = {"number":"3rd","CE":{},"PE":{}}
    oi_chg_highest =  {"PE":{},"CE":{}}
    oi_chg_second_high = {"PE":{},"CE":{}}
    oi_chg_third_high = {"PE":{},"CE":{}}
    for value in sos[time_frame.lower()][expiry]:
        ce = (sos[time_frame.lower()][expiry][value]['CE']['oi'])
        pce =  (sos[time_frame.lower()][expiry][value]['CE']['poi'])
        pe = (sos[time_frame.lower()][expiry][value]['PE']['oi'])
        ppe = (sos[time_frame.lower()][expiry][value]['PE']['poi'])
        ce_chg = int(ce) - int(pce)
        pe_chg = int(pe) - int(ppe)

        if not highest["CE"]:    
            oi_chg_highest["CE"]["value"] = ce_chg
            oi_chg_highest["CE"]["strike"] = value
            oi_chg_second_high["CE"]["value"] = ce_chg
            oi_chg_second_high["CE"]["strike"] = value
            oi_chg_third_high["CE"]["value"] = ce_chg
            oi_chg_third_high["CE"]["strike"] = value
            highest['CE'] = {"highest_side":"CE","highest_value": ce, "strike":value, "other_side" :"PE","other_value":pe,'CMP':lp,'CLOSE':pclose,'poi':pce ,'CMCP':lcp,"other_poi":ppe}
            second_high['CE'] = {"highest_side":"CE","highest_value": 0, "strike":value, "other_side" :"PE","other_value":0,'CMP':lp,'CLOSE':pclose,'poi':pce ,'CMCP':lcp,"other_poi":ppe}
            third_high['CE'] =  {"highest_side":"CE","highest_value": 0, "strike":value, "other_side" :"PE","other_value":0,'CMP':lp,'CLOSE':pclose,'poi':pce ,'CMCP':lcp,"other_poi":ppe}
            
        else:
            oi_chg_first =  oi_chg_highest["CE"]["value"]
            oi_chg_second =  oi_chg_second_high["CE"]["value"]
            oi_chg_third = oi_chg_third_high["CE"]["value"]
            if int(ce_chg) > int(oi_chg_first):
              oi_chg_third_high["CE"] = deepcopy(oi_chg_second_high["CE"])
              oi_chg_second_high["CE"] = deepcopy(oi_chg_highest["CE"])
              oi_chg_highest["CE"] = {"value":ce_chg,"strike":value}
            elif int(ce_chg) > int(oi_chg_second):
              oi_chg_third_high["CE"] = deepcopy(oi_chg_second_high["CE"])
              oi_chg_second_high["CE"] = {"value":ce_chg,"strike":value}
            elif int(ce_chg) > int(oi_chg_third):
               oi_chg_third_high["CE"] = {"value":ce_chg,"strike":value}

            first = highest['CE']['highest_value']
            second  = second_high['CE']['highest_value']
            third = third_high['CE']['highest_value']
            if int(ce) > int(first):
                third_high['CE'] = deepcopy(second_high['CE'])
                second_high['CE'] = deepcopy(highest['CE'])
                highest['CE'] = {"highest_side":"CE","highest_value": ce, "strike":value, "other_side" :"PE","other_value":pe, 'CMP':lp,'CLOSE':pclose,'poi':pce ,'CMCP':lcp,"other_poi":ppe}
            elif int(ce) > int(second) :
                third_high['CE'] = deepcopy(second_high['CE'])
                second_high['CE'] = {"highest_side":"CE","highest_value": ce, "strike":value, "other_side" :"PE","other_value":pe, 'CMP':lp,'CLOSE':pclose,'poi':pce ,'CMCP':lcp,"other_poi":ppe}
            elif int(ce) > int(third): 
                third_high['CE'] = {"highest_side":"CE","highest_value": ce, "strike":value, "other_side" :"PE","other_value":pe, 'CMP':lp,'CLOSE':pclose,'poi':pce ,'CMCP':lcp,"other_poi":ppe} 
                
                
        if not highest["PE"]:
            oi_chg_highest["PE"]["value"] = pe_chg
            oi_chg_highest["PE"]["strike"] = value
            oi_chg_second_high["PE"]["value"] = pe_chg
            oi_chg_second_high["PE"]["strike"] = value
            oi_chg_third_high["PE"]["value"] = pe_chg
            oi_chg_third_high["PE"]["strike"] = value
            highest['PE'] = {"highest_side":"PE","highest_value": pe, "strike":value, "other_side" :"CE","other_value":ce,'CMP':lp,'CLOSE':pclose,'poi':ppe ,'CMCP':lcp,"other_poi":pce}
            second_high['PE'] = {"highest_side":"PE","highest_value": 0, "strike":value, "other_side" :"CE","other_value":0,'CMP':lp,'CLOSE':pclose,'poi':ppe ,'CMCP':lcp,"other_poi":pce}
            third_high['PE'] =  {"highest_side":"PE","highest_value": 0, "strike":value, "other_side" :"CE","other_value":0,'CMP':lp,'CLOSE':pclose,'poi':ppe ,'CMCP':lcp,"other_poi":pce}

        else:
            oi_chg_first =  oi_chg_highest["PE"]["value"]
            oi_chg_second =  oi_chg_second_high["PE"]["value"]
            oi_chg_third = oi_chg_third_high["PE"]["value"]
            if int(pe_chg) > int(oi_chg_first):
              oi_chg_third_high["PE"] = deepcopy(oi_chg_second_high["PE"])
              oi_chg_second_high["PE"] = deepcopy(oi_chg_highest["PE"])
              oi_chg_highest["PE"] = {"value":pe_chg,"strike":value}
            elif int(pe_chg) > int(oi_chg_second):
              oi_chg_third_high["PE"] = deepcopy(oi_chg_second_high["PE"])
              oi_chg_second_high["PE"] = {"value":pe_chg,"strike":value}
            elif int(pe_chg) > int(oi_chg_third):
               oi_chg_third_high["PE"] = {"value":pe_chg,"strike":value}

            first = highest['PE']['highest_value']
            second  = second_high['PE']['highest_value']
            third = third_high['PE']['highest_value']
            if int(pe) > int(first):
                third_high['PE'] = deepcopy(second_high['PE'])
                second_high['PE'] = deepcopy(highest['PE'])
                highest['PE'] = {"highest_side":"PE","highest_value": pe, "strike":value, "other_side" :"CE","other_value":ce, 'CMP':lp,'CLOSE':pclose,'poi':ppe ,'CMCP':lcp,"other_poi":pce}
            elif int(pe) > int(second) :
                third_high['PE'] = deepcopy(second_high['PE'])
                second_high['PE'] = {"highest_side":"PE","highest_value": pe, "strike":value, "other_side" :"CE","other_value":ce, 'CMP':lp,'CLOSE':pclose,'poi':ppe ,'CMCP':lcp,"other_poi":pce}
            elif int(pe) > int(third):
                third_high['PE'] = {"highest_side":"PE","highest_value": pe, "strike":value, "other_side" :"CE","other_value":ce, 'CMP':lp,'CLOSE':pclose,'poi':ppe ,'CMCP':lcp,"other_poi":pce}

    f_list = [highest,second_high,third_high]
    strike_list= {}
    strike_list["PE"] = [int(oi_chg_highest["PE"]["strike"]),int(oi_chg_second_high["PE"]["strike"]),int(oi_chg_third_high["PE"]["strike"])]
    strike_list["CE"] = [int(oi_chg_highest["CE"]["strike"]),int(oi_chg_second_high["CE"]["strike"]),int(oi_chg_third_high["CE"]["strike"])]
    await condition_check(f_list,asset,expiry,lp,time_frame,lcp,strike_list)
    #return f_list

async def check_poi_diff(oi,poi,ooi,opoi):
  try:
    mside = int(oi) - int(poi)
    oside = int(ooi) - int(opoi)
    if mside > oside:
      return 1
    else:
      return 0
  except Exception as e:
     print("osososososososososososososos: ",str(e))



async def check_lower_strike(asset,time_frame,strike,side):
   try:
        return 1
        asset_name = asset.upper()+time_frame.upper()
        asset_table = db[asset_name]
        print(asset_name,strike,side)
        new_list = list(asset_table.find({"side":side.upper()}).sort("strike",-1))

        #print("sssssssssssssssssssssssssss",lot_check)
        #lot_size = int(lot_check[0]['lot'])
        #new_strike = int(strike)- int(lot_size)
        #new_list = list(asset_table.find({"strike":new_strike}))
        #print(new_list)
        x = 0
        for nl in new_list:
            if x == 1:
              x = 2
              print(nl)
              if nl['oi'] < 1 and nl['oi'] != -1:
                  return 1
              else:
                  return 0
            if nl['strike'] == strike:
               x = 1
        return 0
   except Exception as e:
      print("oooooooooooooooooooooooooooo",str(e))
async def condition_check(f_list,asset,expiry,lp,time_frame,lcp,strike_list):
	now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
	cur_time = (now.strftime('%H:%M:%S'))

	for f in f_list:
          print("-----------------------:",asset,expiry,time_frame,f)
          if int(f["CE"]["strike"]) in strike_list["CE"]:
             strike_test_ce = 1
          else:
             strike_test_ce = 0
          if int(f["PE"]["strike"]) in strike_list["PE"]:
             strike_test_pe = 1
          else:
             strike_test_pe = 0
          ce_lower_strike_flag = await check_lower_strike(asset,time_frame,f['CE']['strike'],f['CE']['other_side'])
          pe_lower_strike_flag = await check_lower_strike(asset,time_frame,f['PE']['strike'],f['PE']['other_side'])
          print(ce_lower_strike_flag, pe_lower_strike_flag)
          ce_poi_diff = await check_poi_diff(f['CE']['highest_value'],f['CE']['poi'], f['CE']['other_value'], f['CE']['other_poi'])
          pe_poi_diff = await check_poi_diff(f['PE']['highest_value'],f['PE']['poi'], f['PE']['other_value'], f['PE']['other_poi'])
          number = f['number']
          if f['CE']['highest_value'] != -1  and f['CE']['other_value'] != -1 and f['CE']['highest_value'] > float(f['CE']['poi']) and ce_lower_strike_flag == 1 and ce_poi_diff == 1 and strike_test_ce == 1:
           print(f['PE'])
           print(f['CE'])
           if int(f['CE']['highest_value']) > 2*(f['CE']['other_value']):
             ratio = int(int(f['CE']['highest_value'])/int(f['CE']['other_value']))
             price_difference = abs( (float(f['CE']['strike']) - float(lp)) / float(f['CE']['strike']) )
             if lcp != 0:
               cash_price_difference =  abs( (float(f['CE']['strike']) - float(lcp)) / float(f['CE']['strike']) )
             else:
               cash_price_difference = 0.0010
             #print(price_difference) 
             if price_difference <= 0.0015 and cash_price_difference <= 0.0015:
               print(" CE Alert", asset)
               table = db["alertCheck2"]
               in_table = table.update_one({asset:0}, {'$set':{asset: 1}})
               #print(in_table)
               #try:
                #  with open("alerts.txt","a") as file:
                 #     file.write(asset+ str(lp)+ str(f)+"\n")
               #except Exception as e:
                #  print(e)
               await send_alert({"number":number,"at_time":str(cur_time),"name":asset,"ratio":ratio,"expiry":expiry,"time":time_frame, "values":f["CE"]})
             else:
               print("CE Price Differnece more than 0.15 percent (0.0015)", price_difference)
           else:
             print("Highest CE value difference not enough")

          if f['PE']['highest_value'] != -1 and f['PE']['other_value'] != -1 and  f['PE']['highest_value'] >  float(f['PE']['poi']) and pe_lower_strike_flag == 1 and pe_poi_diff == 1 and strike_test_pe == 1:
            if int(f['PE']['highest_value']) > 2*(f['PE']['other_value']):
              ratio = int(int(f['PE']['highest_value'])/int(f['PE']['other_value']))
              price_difference = abs( (float(f['PE']['strike']) - float(lp)) / float(f['PE']['strike']) )
              if lcp != 0:
                cash_price_difference =  abs( (float(f['PE']['strike']) - float(lcp)) / float(f['PE']['strike']) )
              else:
                cash_price_difference = 0.0010
              #print(price_difference)
              if price_difference <= 0.0015 and cash_price_difference  <= 0.0015:
                print(" PE Alert", asset)
                table = db["alertCheck2"]
                in_table = table.update_one({asset:0}, {'$set':{asset: 1}})
                #print(in_table)
                #try:
                 # with open("alerts.txt","a") as file:
                  #   file.write(asset+ str(lp)+ str(f)+"\n")
                #except Exception as e:
                 #   print(e)
                await send_alert({"number":number,"at_time":str(cur_time),"name":asset,"ratio":ratio,"expiry":expiry,"time":time_frame, "values":f["PE"]})
              else:
                print("PE Price Differnece more than 0.15 percent (0.0015)", price_difference)
            else:
              print("Highest PE value difference not enough")

