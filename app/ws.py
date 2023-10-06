from dbhelp import send_alert
import time
import asyncio
x = 0
while True:
 time.sleep(1)
 x += 1
 asyncio.run(send_alert({"tests":x}))
 if x >= 2:
  break
