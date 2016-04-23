#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
import hub
from chest import Chest
from flask import request
from flask import json
from flask import abort
from hub import app
from dealer import sensor_data_collector

nodes = Chest()

@app.route('/sensors/<int:uuid>/data', methods=['GET'])
def sensor_data(uuid):
    global nodes
    #uuid = str(uuid)
    return str(nodes.data)

@app.route('/sensors/activate', methods=['GET'])
def activate_sensor(payload = None):
    """API call to activate a sensor on the hub.
    The sensor should contain a parameter fo it's \
    IP address as "ip", uuid as "id"
    """

    global nodes
    
    uuid = int(request.args.get("id").replace("/",""))
    ip = request.args.get("ip")
    port = 80
    conf_data = hub.conf.read_data()

    #TODO make dynamic registering by going through different GPIO
    # ports and when you get a response that's the type
    if uuid in conf_data.keys():
        with nodes.lock:
            # THIS REQUIRES NODES THREADS TO REMOVE THEMSELVES
            if uuid in nodes.data:
                return json.jsonify({"message": str(uuid)
                                    + " was already activated"})
            nodes.data[uuid] = {
                    "uuid": uuid,
                    "ip"  : ip,
                    "type": "temp",
                    "port": port
            }
    thread.start_new_thread(sensor_data_collector, (uuid, ip, "temp"))

    return json.jsonify({"message": str(uuid) + " has been activated."})

    #TODO Log the fact that the sensor must be registered.
    #abort(400)

@app.route('/sensors/list')
def sensors_list():
    """Return a json of the sensors that are currently active
    :returns: TODO
    """

    global nodes
    return json.jsonify(nodes.data)
