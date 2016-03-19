#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Gmail_Send import send_email
import flask
import sys
from flask import Flask
from flask import request
from flask import json
app = Flask(__name__)

SND_PASSWD = ""

@app.route('/')
def sensor_recv():
    """Webpage that takes parameter 'data' from a 
    sensor in json format. 
    Current emails the data out. Eventually will update webpage
    or queue up data.
    """
    str_data = request.args.get('data')
    json_data = json.loads(str_data)
    send_email(json.dumps(json_data,
                          sort_keys = True,
                          indent = 2,
                          separators=(',', ':')
                         ),
              "Sensor Data",
              snd_psswd = SND_PASSWD
              )
    return "Message sent"

if __name__ == '__main__':
    SND_PASSWD = sys.argv[1]
    #app.run(host="192.168.0.1") #need to test this
    app.run(debug=True)
