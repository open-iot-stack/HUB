#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Gmail import send_email
from ConfigManager import Config
import flask
import sys
import getopt
import time
import thread
import requests
import octopifunctions as octopi
from Logger import Log
from message_generator import MessageGenerator
from channel import Channel
from flask import Flask
from flask import request
from flask import json
from flask import render_template
from flask import url_for
from flask import abort
#import libs
from urllib2 import Request, urlopen
from json import dumps

app = Flask(__name__)

SND_PASSWD = ""
API_KEY = octopi.testingApiKey

nodes = {}
nlock = thread.allocate_lock()

printers = {}
plock = thread.allocate_lock()

conf = Config()
send_channel, recv_channel = Channel()

def get_temp(node_ip, gpio):
        """Creates request to dht sensor for data"""
    req = Request(node_ip+"/"+gpio+"/dht")
    response_body = urlopen(req).read()
    data = json.loads(response_body)
    temp = data['data']['temp']
    humidity = data['data']['humi']
    print("temp: "+temp+" humidity: "+ humi)

    return data

def sensor_data_collector(uuid, ip, pertype):
    """Should spawn as its own thread for each sensor
    that calls activate. Collects data from the sensor every
    second and dumps it into the send channel.
    """

    global nodes
    global nlock
    global send_channel
    global log
    #TODO fix url to be the correct call based on type
    #url = "http://" + ip + "/GPIO/2"
    #TODO a lot of this code is fulling working/tested but general idea is there
    while(True):
        # load the json from the chip
        try:
            #response = requests.get(url, timeout=3)
                        #need to find how we're getting the node_ip and fill in.
                        response = get_temp(node_ip, 1)
        except requests.RequestException:
            with nlock:
                if (ip == nodes[uuid]["ip"]):
                    log.log("ERROR: Lost Connection to "
                            + uuid + ". Thread exiting...")

                    if nodes.has_key(uuid):
                        nodes.pop(uuid)
            thread.exit()
        if response.status_code != requests.codes.ok:
            log.log("ERROR: Response from "
                    + uuid + " returned status code "
                    + response.status_code)
        else:
            if response.headers.get('content-type') != 'application/json':
                log.log("ERROR: Response from "
                        + uuid + " was not in json format")

            r_json = response.json()
            if (uuid != r_json.get("uuid")):
                # TODO: Make a get request on the chip
                # telling it to reconnect
                thread.exit()
            send_channel.send({
                uuid: {
                    pertype : r_json.get("data")
                } 
            })
        time.sleep(1)

def data_receiver():
    """Should spawn as its own thread. Will take data that
    is collected by the sensors and send it to the Web API.
    Also is in charge of logging data based on UUID.
    """
    global recv_channel
    for message in MessageGenerator(recv_channel):
        print message
    #pass

def printer_data_receiver(uuid, ip, port, key):
    global printers
    global plock
    url = ip + ":" + port
    while(True):
        response = octopi.GetJobInfo(url, key)
        #TODO Add data into send channel. Talk to Aaron about change
        # changing responses from jobs to just be the pure response
        sleep(1)

@app.route('/printers/list')
def printers_list():
    """Returns a json of currently active printers
    :returns: TODO
    """

    global printers
    return json.jsonify(printers)

@app.route('/printers/<int:uuid>/<action>',methods=['POST', 'GET'])
def print_action(uuid, action):
    """Post request to do a print action. UUID must match a printer
    type in the config file
    """

    global printers
    uuid = str(uuid)
    if not printers.has_key(uuid):
        abort(400)
    printer = printers.get(uuid)

    ip   = printer.get("ip")
    port = printer.get("port")
    key  = printer.get("key")
    url  = ip + ":" + port

    #TODO make helper function for actions to respond the web api
    # with the actual success as the command. For now just spawn command
    # as new thread
    if action == "start":
        #response = octopi.StartCommand(url, key)
        start_new_thread(octopi.StartCommand, (url, key))
        pass
    elif action == "pause":
        #response = octopi.PauseUnpauseCommand(url, key)
        start_new_thread(octopi.PauseUnpauseCommand, (url, key))
        pass
    elif action == "cancel":
        #response = octopi.CancelCommand(url, key)
        start_new_thread(octopi.CancelCommand, (url, key))
        pass
    return json.jsonify({"message": action + " successfully sent to the printer."})

@app.route('/printers/<int:uuid>/status', methods=['GET'])
def print_status(uuid):
    global printers
    uuid = str(uuid)
    if not printers.has_key(uuid):
        abort(400)
    printer = printers.get(uuid)

    ip   = printer.get("ip")
    port = printer.get("port")
    key  = printer.get("key")
    url  = ip + ":" + port

    response = octopi.GetJobInfo(url, key)
    #TODO return the actual data that's useful for the web api
    return response.read()


@app.route('/printers/activate', methods=['GET'])
def activate_printer(payload = None):
    """API call to activate a printer on the hub.
    The printer should provide a parameter 'payload' in
    json format that contains it's IP address as "ip",
    uuid as "uuid", port as "port", and apikey as "key"
    :returns: TODO
    """

    global printers
    global plock
    if payload == None:
        str_payload = request.args.get("payload")
        payload     = json.loads(str_payload)

    uuid = payload.get("uuid")
    ip   = payload.get("ip")
    port = payload.get("port", "80")
    key  = payload.get("key", "0")

    with plock:
        printers[uuid] = {
                "ip": ip,
                "port": port,
                "key": key
        }

    return json.jsonify(printers)

@app.route('/sensors/<int:uuid>/data', methods=['GET'])
def sensor_data(uuid):
    global nodes
    global nlock
    uuid = str(uuid)
    return str(nodes)

@app.route('/sensors/activate', methods=['GET'])
def activate_sensor(payload = None):
    """API call to activate a sensor on the hub.
    The sensor should provide a parameter 'payload' in
    json format that contains it's IP address as "ip",
    uuid as "uuid", and port as "port"
    :returns: TODO
    """

    global nodes
    global nlock
    if payload == None:
        str_payload = request.args.get('payload')
        payload     = json.loads(str_payload)

    uuid = payload.get("uuid")
    ip   = payload.get("ip")
    port = payload.get("port", "80")
    conf_data = conf.read_data()

    #TODO make dynamic registering by going through different GPIO
    # ports and when you get a response that's the type
    if uuid in conf_data.keys():
        pertype = conf_data.get(uuid)
        with nlock:
            nodes[uuid] = {
                    "ip": ip,
                    "type": pertype,
                    "port": port
            }
        thread.start_new_thread(sensor_data_collector, (uuid, ip, pertype))
        return json.jsonify(nodes)

    #TODO Log the fact that the sensor must be registered.
    abort(400)

@app.route('/register', methods=['GET', 'POST'])
def register_peripheral():
    """Webpage to register the type of a given sensor
    This should be done before activating the sensor.
    :returns: webpage of result
    """

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        uuid = request.form.get('uuid')
        pertype = request.form.get('pertype')
        if request.form.get('is_update'):
            success = conf.update_data({uuid: pertype})
        else:
            success = conf.add_data({uuid: pertype})

        if success:
            return json.jsonify({"message": uuid + " has been registered as " + pertype})
        else:
            return json.jsonify({"message": uuid + " was not registered, are you updating?"})

    abort(405)

@app.route('/')
def index():
    uuid=0
    return "0 represents the UUID" + '<br>'\
         + url_for('register_peripheral') + '<br>'\
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

def main(argv):
    debug         = False
    port          = None
    host          = None
    threaded      = False
    print_enabled = False
    global API_KEY
    global SND_PASSWD
    global log
    try:
        opts, args = getopt.getopt(argv, "hdtvp:a:",
                ["apikey=","pass=","help","port=","debug","host=","threaded","verbose"])
    except getopt.GetoptError, err:
        # Print debug info
        print str(err)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print "Usage: Server.py"\
            + "\n    -a/--apikey <apikey>"\
            + "\n    -p/--port   <port>"\
            + "\n       --pass   <password>"\
            + "\n       --host   <ip address>"\
            + "\n    -d/--debug"\
            + "\n    -h/--help"\
            + "\n    -t/--threaded"\
            + "\n    -v/--verbose"
            sys.exit(0)
        elif opt in ["-a", "--apikey"]:
            global API_KEY
            API_KEY = arg
        elif opt in ["--pass"]:
            global SND_PASSWD
            SND_PASSWD = arg
        elif opt in ["-p", "--port"]:
            port = int(arg)
        elif opt in ["-d", "--debug"]:
            debug = True
        elif opt in ["--host"]:
            host = arg
        elif opt in ["-t", "--threaded"]:
            threaded = True
        elif opt in ["-v", "--verbose"]:
            print_enabled = True

    log = Log(print_enabled=print_enabled)

    thread.start_new_thread(data_receiver, ())
    app.run(host=host, debug=debug, port=port,threaded=threaded)

if __name__ == '__main__':
    main(sys.argv[1:])
