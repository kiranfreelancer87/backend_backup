import pandas as pd
import csv
import pymongo
import requests
url = "https://api.kite.trade/instruments"
response = requests.get(url)
open("csv/instruments.csv", "wb").write(response.content)

cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/") 
#df = pd.read_csv('csv/fo.csv')
#all_sym = df["SYMBOL \n"].tolist()
all_sym = ["NIFTY","BANKNIFTY"]
price_tokens = []
cash_price_tokens = []
all_tokens  = []
all_inst = []
alert_check = []
def seperate(token):
  try:
    global cash_price_tokens
    global price_tokens
    global all_tokens
    global all_inst
    if token == "NIFTY":
      expiry_check = "2023-10-05"
    else:
      expiry_check = "2023-10-04"
    monthly_list = []
    weekly_list = []
    token = token.upper()
    n = len(token)+3
    df = pd.read_csv('csv/instruments.csv')
    ff = df[df['name'] == token]
    sf = ff[ff['segment'] == "NFO-OPT"]
    m_f = sf[(sf['expiry'] == expiry_check) | (sf['expiry'] == expiry_check)]
    #print(m_f)
    tokens= m_f["instrument_token"].tolist()
    #print(tokens)
 
    with open ("csv/"+token+".csv","w",newline="") as f:
        write = csv.writer(f)
        for tk in tokens:
            write.writerow([tk])

    all_tokens = all_tokens + tokens
    print("---------------------")
    pf = df[df['tradingsymbol'] == token+"23OCTFUT"]
    ptoken  = pf['instrument_token'].tolist()
    print(ptoken)
    price_tokens.append({"id":ptoken[0],"name":token,"CMP":0,"CLOSE":-1,"expiry":expiry_check})
    ccpf = df[df['segment'] == "INDICES"]
    if token == "NIFTY":
      cashtoken = "NIFTY 50"
    elif token == "BANKNIFTY":
      cashtoken = "NIFTY BANK"
    cpf = ccpf[ccpf['tradingsymbol'] == cashtoken]
    cptoken = cpf['instrument_token'].tolist()
    print(cptoken)
    #print("ssssssssssssssssssssssssssssssssssssssssssssssssssssss")
    try:
     cash_price_tokens.append({"id":cptoken[0],"name":token,"CMP":0,"CLOSE":-1})
    except:
     pass
    #print("ssss : ",m_f)
    #print("ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
    tw = []
    tm= []
    for row_tuple in m_f.itertuples():
            #print(row_tuple[3][n:n+2])
            if (row_tuple[3][n:n+2]).isnumeric():
                all_inst.append({"id":row_tuple[1],"asset":row_tuple[4],"frame":"WEEKLY","table":row_tuple[4]+"WEEKLY","expiry":row_tuple[6],"lot":row_tuple[9]})
                weekly_list.append({"period":"weekly","id":row_tuple[1], "name":row_tuple[3], "asset":row_tuple[4], "expiry":row_tuple[6], "strike":row_tuple[7], "side":row_tuple[10],"oi":-1,"lp":0,"poi":-1,"lot":row_tuple[9],"chg":-1})
                tw.append(row_tuple)
            else:
                all_inst.append({"id":row_tuple[1],"asset":row_tuple[4],"frame":"MONTHLY","table":row_tuple[4]+"MONTHLY","expiry":row_tuple[6], "lot":row_tuple[9]})
                monthly_list.append({"period":"monthly","id":row_tuple[1], "name":row_tuple[3], "asset":row_tuple[4], "expiry":row_tuple[6], "strike":row_tuple[7], "side":row_tuple[10],"oi":-1,'lp':0,"poi":-1,"lot":row_tuple[9],"chg":-1})
                tm.append(row_tuple)
    weekly = pd.DataFrame(tw)
    monthly = pd.DataFrame(tm)
   
    db = cl.zerodha_index
    #print("================")
    if len(tw) > 0:
        #pass
        db[token+"WEEKLY"].drop()
        
        table = db[token+"WEEKLY"]
    
        result = table.insert_many(weekly_list)
    if len(tm) > 0 :
        #pass
        db[token+"WEEKLY"].drop()
        table = db[token+"WEEKLY"]
        result = table.insert_many(monthly_list)
  except Exception as e:
     print(str(e))
for sym in all_sym:
    print(sym)
    alert_check.append({sym:0})
    seperate(sym)

with open ("csv/token_list.csv","w",newline="") as f:
    write = csv.writer(f) 
    for token in all_tokens:
        write.writerow([token])
        
db = cl.zerodha_index

db['alerts'].drop()

db["allList"].drop()
table = db['allList']
result = table.insert_many(all_inst)

db['alertCheck'].drop()
table = db['alertCheck']
result = table.insert_many(alert_check)

db['alertCheck1'].drop()
table = db['alertCheck1']
result = table.insert_many(alert_check)

db['alertCheck2'].drop()
table = db['alertCheck2']
result = table.insert_many(alert_check)

db['alertCheck3'].drop()
table = db['alertCheck3']
result = table.insert_many(alert_check)

db['priceList'].drop()
table = db['priceList']
result = table.insert_many(price_tokens)

db['cashPriceList'].drop()
table = db['cashPriceList']
result = table.insert_many(cash_price_tokens)
