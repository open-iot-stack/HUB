#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Gmail_Send import send_email
from ConfigManager import Config
import flask
import sys
import time
import urllib2
import thread
from message_generator import MessageGenerator
from channel import Channel
from flask import Flask
from flask import request
from flask import json
from flask import render_template
from flask import url_for
app = Flask(__name__)

SND_PASSWD = ""

nodes = {}
nlock = thread.allocate_lock()
conf = Config()
send_channel, recv_channel = Channel()

def data_collector(uuid, ip, chiptype):
    global nodes
    while(True):
        # load the json from the chip
        try:
            response = urllib2.urlopen("http://" + ip, timeout=3)
        except urllib2.URLError:
            with nlock:
                if (ip == nodes[uuid]["ip"]):
                    print "ERROR: Lost Connection to "\
                            + uuid + ". Thread exiting..."
                    if nodes.has_key(uuid):
                        nodes.pop(uuid)
            thread.exit()
        str_payload = response.read()
        json_payload = json.loads(str_payload)
        if (uuid != json_payload["UUID"]):
            # TODO: Make a get request on the chip telling it to reconnect
            pass
        send_channel.send(json_payload)
        time.sleep(1)

def data_receiver():
    for message in MessageGenerator(recv_channel):
        print message
    #pass

@app.route('/printers/<int:uuid>/<action>',methods=['POST'])
def print_action(uuid, action):
    """Post request to do a print action. UUID must match a printer
    type in the config file
    """
    if action == "start":
        pass
    elif action == "pause":
        pass
    elif action == "cancel":
        pass
    elif action == "status":
        pass
    return action

@app.route('/sensors/<int:uuid>/data', methods=['GET'])
def sensor_data(uuid):
    return str(uuid)

@app.route('/activate')
def activate_sensor():
    """API call to register a sensor.
    The UUID and IP should be provided in json format
    as a variable "payload"
    :returns: TODO
    """

    global nodes
    str_payload = request.args.get('payload')
    json_payload = json.loads(str_payload)
    uuid = json_payload["UUID"]
    ip = json_payload["IP"]
    conf_data = conf.read_data()
    if uuid in conf_data.keys():
        chiptype = conf_data[uuid]
        with nlock:
            nodes[uuid] = {
                    "ip": ip,
                    "type": chiptype
            }
        thread.start_new_thread(data_collector, (uuid, ip, chiptype))
        return str(nodes)
    return str(nodes)

@app.route('/register',methods=['GET', 'POST'])
def register_sensor():
    """Webpage to register the type of a given sensor
    This should be done before activating the sensor.
    :returns: webpage of result
    """

    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        uuid = request.form['uuid']
        chiptype = request.form['chiptype']
        if request.form.get('is_update'):
            success = conf.update_data({uuid: chiptype})
            return str(success)
        else:
            success = conf.add_data({uuid: chiptype})
            return str(success)


@app.route('/')
def index():
    uuid=0
    return "0 represents the UUID" + '<br>'\
         + url_for('register_sensor') + '<br>'\
         + url_for('activate_sensor') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='start') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='cancel') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='pause') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='status') + '<br>'\
         + url_for('sensor_data'  ,uuid=uuid) + '<br>'
#    send_email(json.dumps(json_data,
#                          sort_keys = True,
#                          indent = 2,
#                          separators=(',', ':')
#                         ),
#              "Sensor Data",
#              snd_psswd = SND_PASSWD
#              )
    return "Message sent"

if __name__ == '__main__':
    #SND_PASSWD = sys.argv[1]
    #app.run(host="192.168.0.1") #need to test this
    app.run(debug=True)
