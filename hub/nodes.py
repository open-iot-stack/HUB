#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
import hub
from flask import request
from flask import json
from flask import abort
from hub import app
from dealer import sensor_data_collector

nodes = {}
nlock = thread.allocate_lock()

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
    conf_data = hub.conf.read_data()

    #TODO make dynamic registering by going through different GPIO
    # ports and when you get a response that's the type
    if uuid in conf_data.keys():
        pertype = conf_data.get(uuid)
        with nlock:
            # THIS REQUIRES NODES THREADS TO REMOVE THEMSELVES
            if uuid in nodes:
                return json.jsonify({"message": uuid + " was already activated"})
            nodes[uuid] = {
                    "ip": ip,
                    "type": pertype,
                    "port": port
            }
        thread.start_new_thread(sensor_data_collector, (uuid, ip, pertype))
        return json.jsonify({"message": uuid + " has been activated."})

    #TODO Log the fact that the sensor must be registered.
    abort(400)

@app.route('/sensors/list')
def sensors_list():
    """Return a json of the sensors that are currently active
    :returns: TODO
    """

    return json.jsonify(nodes)
