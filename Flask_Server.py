#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Gmail_Send import send_email
from ConfigManager import Config
import flask
import sys
import getopt
import time
import thread
import requests
from message_generator import MessageGenerator
from channel import Channel
from flask import Flask
from flask import request
from flask import json
from flask import render_template
from flask import url_for
app = Flask(__name__)

SND_PASSWD = ""
API_KEY = ""


nodes = {}
nlock = thread.allocate_lock()

printers = {}
plock = thread.allocate_lock()

conf = Config()
send_channel, recv_channel = Channel()

def data_collector(uuid, ip, pertype):
    """Should spawn as its own thread for each sensor
    that calls activate. Collects data from the sensor every
    second and dumps it into the send channel.
    """

    global nodes
    url = "http://" + ip + "/GPIO/2"
    while(True):
        # load the json from the chip
        try:
            response = requests.get(url, timeout=3)
        except requests.RequestException:
            with nlock:
                if (ip == nodes[uuid]["ip"]):
                    print "ERROR: Lost Connection to "\
                            + uuid + ". Thread exiting..."
                    if nodes.has_key(uuid):
                        nodes.pop(uuid)
            thread.exit()
        if response.status_code != requests.codes.ok:
            print "ERROR: Response from "\
                    + uuid + " returned status code " + response.status_code
        else:
            if r.headers.get('content-type') != 'application/json':
                print "ERROR: Response from "\
                        + uuid + " was not in json format"
            r_json = response.json()
            if (uuid != r_json["UUID"]):
                # TODO: Make a get request on the chip telling it to reconnect
                thread.exit()
            send_channel.send({
                uuid: {
                    pertype : r_json["DATA"]
                } 
            })
        time.sleep(1)

def data_receiver():
    """Should spawn as its own thread. Will take data that
    is collected by the sensors and send it to the Web API.
    Also is in charge of logging data based on UUID.
    """

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

@app.route('/activate', methods=['GET'])
def activate_peripheral():
    """API call to register a sensor.
    The UUID and IP should be provided in json format
    as a variable "payload"
    :returns: TODO
    """

    global nodes
    global printers
    str_payload = request.args.get('payload')
    json_payload = json.loads(str_payload)
    uuid = json_payload["UUID"]
    ip = json_payload["IP"]
    conf_data = conf.read_data()
    if uuid in conf_data.keys():
        pertype = conf_data[uuid]
        if pertype == "printer":
            with plock:
                printers[uuid] = {
                        "ip": ip,
                        "type": pertype
                }
            return str(printers)
        else:
            with nlock:
                nodes[uuid] = {
                        "ip": ip,
                        "type": pertype
                }
            thread.start_new_thread(data_collector, (uuid, ip, pertype))
            return str(nodes)
    return str(False)

@app.route('/register', methods=['GET', 'POST'])
def register_peripheral():
    """Webpage to register the type of a given sensor
    This should be done before activating the sensor.
    :returns: webpage of result
    """

    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        uuid = request.form['uuid']
        pertype = request.form['pertype']
        if request.form.get('is_update'):
            success = conf.update_data({uuid: pertype})
            return str(success)
        else:
            success = conf.add_data({uuid: pertype})
            return str(success)


@app.route('/')
def index():
    uuid=0
    return "0 represents the UUID" + '<br>'\
         + url_for('register_peripheral') + '<br>'\
         + url_for('activate_peripheral') + '<br>'\
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

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ha:p:", ["apikey","pass","help"])
    except getopt.GetoptError, err:
        # Print debug info
        print str(err)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "Usage: run.py -a <apikey> -p <gmail pass>"
            sys.exit(0)
        elif opt in ("-a", "--apikey"):
            global API_KEY
            API_KEY = arg
        elif opt in ("-p", "--pass"):
            global SND_PASSWD
            SND_PASSWD = arg
    #app.run(host="192.168.0.1") #need to test this
    app.run(debug=True)

if __name__ == '__main__':
    main(sys.argv[1:])
