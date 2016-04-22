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

@app.route('/sensors/<int:id>/data', methods=['GET'])
def sensor_data(id):
    global nodes
    #uuid = str(uuid)
    return str(nodes.data)

@app.route('/sensors/activate', methods=['GET'])
def activate_sensor(payload = None):
    """API call to activate a sensor on the hub.
    The sensor should provide a parameter 'payload' in
    json format that contains it's IP address as "ip",
    id as "id", and port as "port"
    :returns: TODO
    """

    global nodes
    if payload == None:
        str_payload = request.args.get('payload')
        payload     = json.loads(str_payload)

    id   = request.args.get("id")
    ip   = request.args.get("ip")
    port = int(request.args.get("port", 80))
    conf_data = hub.conf.read_data()

    #TODO make dynamic registering by going through different GPIO
    # ports and when you get a response that's the type
    if id in conf_data.keys():
        pertype = conf_data.get(id)
        with nodes.lock:
            # THIS REQUIRES NODES THREADS TO REMOVE THEMSELVES
            if id in nodes.data:
                return json.jsonify({"message": str(id)
                                    + " was already activated"})
            nodes.data[id] = {
                    "id":   id,
                    "ip"  : ip,
                    "type": pertype,
                    "port": port
            }
        thread.start_new_thread(sensor_data_collector, (id, ip, pertype))
        return json.jsonify({"message": str(id) + " has been activated."})

    log.log("ERROR: Node " + str(id) + " tried to activate but was never registered")
    abort(400)

@app.route('/sensors/list')
def sensors_list():
    """Return a json of the sensors that are currently active
    :returns: TODO
    """

    global nodes
    return json.jsonify(nodes.data)
