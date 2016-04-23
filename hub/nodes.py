#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
import hub
from chest import Chest
from flask import request
from flask import json
from flask import abort
from hub import app
from dealer import node_data_collector

nodes = Chest()

@app.route('/nodes/<int:id>', methods=['GET'])
def node_data(id):
    with nodes.lock:
        if id in nodes.data:
            return json.jsonify(nodes.data.get(id).copy())
    abort(400)

@app.route('/nodes/activate', methods=['GET'])
def activate_node(payload = None):
    """API call to activate a node on the hub.
    The node should provide a parameter 'payload' in
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
        thread.start_new_thread(node_data_collector, (id, ip, pertype))
        return json.jsonify({"message": str(id) + " has been activated."})

    log.log("ERROR: Node " + str(id) + " tried to activate but was never registered")
    abort(400)

@app.route('/nodes', methods=['GET'])
def nodes_list():
    """Return a json of the nodes that are currently active
    :returns: TODO
    """

    return json.jsonify(nodes.data.copy())
