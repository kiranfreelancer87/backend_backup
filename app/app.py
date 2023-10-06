from flask import Flask, render_template, request
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
data = {}
flag =0

@app.route('/',methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/test',methods=['GET'])
def index1():
    return render_template("index1.html")

   
@app.route('/alert',methods=['POST'])
def alert():
    global data
    global flag
    data = request.get_json(force=True)
    flag = 1
    print(data)
    return '1'

@sock.route('/echo')
def echo(sock):
    global data
    global flag
    while True:
        if flag == 1:
            sock.send(data)
            flag = 0
            
            
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80,ssl_context='adhoc')
