from dbhelp import telegram_alert

raw = {'number': '2nd', 'at_time': '15:20:33', 'name': 'INDIACEM', 'ratio': 4, 'expiry': '2022-12-29', 'time': 'MONTHLY', 'values': {'highest_side': 'PE', 'highest_value': 751100, 'strike': 230.0, 'other_side': 'CE', 'other_value': 182700, 'CMP': 230.2, 'CLOSE': 240.5, 'poi': 669900, 'CMCP': 229.8}}
newline = "\n"
alert = "Time : "+str(raw['at_time'])+newline+ \
        "Name : "+raw['name']+newline + \
        "Strike : "+ str(raw['values']['strike'])+newline+ \
        "Expiry : " + raw['expiry']+newline+ \
        "Number: "+ str(raw['number'])+newline+ \
        "Oi Diff : " +str(raw['ratio'])+" times"+newline+ \
        "Oi VALUES"+newline+ \
        "High Side : "+ str(raw['values']['highest_side'])+", OI : "+str(raw['values']['highest_value'])+newline+ \
        "Low Side  : "+ str(raw['values']['other_side'])+", OI : "+str(raw['values']['other_value'])+newline+ \
        "CMP : "+ str(raw['values']['CMP']) 
telegram_alert(alert)
