import subprocess, signal
import datetime
from dateutil.tz import gettz

while True:
    #break
    dtobj = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    a = dtobj.time()
    b = datetime.time(9,14,20)
    if a > b:
        break

subprocess.Popen(['python3', '/home/app/cash_price.py'],
                 stdin=subprocess.DEVNULL,
                 stdout=open('/home/app/logs/cash_price.out', 'w'),
                 stderr=subprocess.STDOUT,
                 start_new_session=True)


subprocess.Popen(['python3', '/home/app/price.py'],
                 stdin=subprocess.DEVNULL,
                 stdout=open('/home/app/logs/price.out', 'w'),
                 stderr=subprocess.STDOUT,
                 start_new_session=True)

subprocess.Popen(['python3', '/home/app/3.py','BANKNIFTY'],
                 stdin=subprocess.DEVNULL,
                 stdout=open('/home/app/logs/BANK.out', 'w'),
                 stderr=subprocess.STDOUT,
                 start_new_session=True)
#    #             preexec_fn=(lambda: signal.signal(signal.NOHUP, signal.SIG_IGN)))

subprocess.Popen(['python3', '/home/app/3.py','NIFTY'],
                 stdin=subprocess.DEVNULL,
                 stdout=open('/home/app/logs/nifty.out', 'w'),
                 stderr=subprocess.STDOUT,
                 start_new_session=True)
