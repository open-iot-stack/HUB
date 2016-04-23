#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
import hub
from chest import Chest
from flask import request, json, abort
from hub import app
from dealer import node_data_collector
from database import db_session
from models import Sensor, Node

nodes = Chest()

@app.route('/nodes/<int:node_id>', methods=['GET'])
def node_data(node_id):
    result = Node.query.filter_by(id=node_id).first()
    if result is None:
        abort(404)
    d = {'id': result.id,
         'ip': result.ip}
    return jsonify(classes=d)

@app.route('/nodes/activate', methods=['GET'])
def activate_node(payload = None):
    """API call to activate a node on the hub.
    The node should provide a parameter 'payload' in
    json format that contains it's IP address as "ip",
    id as "id", and port as "port"
    :returns: TODO
    """

    global nodes
    id   = int(request.args.get("id"))
    ip   = request.args.get("ip")
    port = int(request.args.get("port", 80))
    conf_data = hub.conf.read_data()
    log = hub.log

    anode = Node(id, ip)
    db_session.add(anode)
    db_session.commit()

    result = Node.query.filter_by(id=id).first()
    if result:
        thread.start_new_thread(node_data_collector, (id, ip))
        return json.jsonify({"message": str(id) + " has been activated."})

    log.log("ERROR: Node " + str(id) + " tried to activate but was never registered")
    abort(400)

@app.route('/nodes', methods=['GET'])
def nodes_list():
    """Return a json of the nodes that are currently active
    :returns: TODO
    """

    results = Node.query.all()
    json_results = []
    for result in results:
        d = {'id': result.id,
             'ip': result.ip}
        json_results.append(d)
    return json.jsonify(nodes = json_results)


@app.route('/nodes/trigger/callback', methods=['GET'])
def nodes_trigger_callback():
    """Return a json of the nodes that are currently active
    :returns: TODO
    """
    id   = int(request.args.get("id"))
    pin  = int(request.srgs.get("pin"))
    data = int(request.args.get("data"))

    d = {'id': id,
         'ip': pin,
         'data': data}
    return json.jsonify(d)


@app.route('/nodes/<int:nid>/sensors', methods=['GET', 'POST'])
def node_sensors(nid):
    """
        List Sensors Attached to Node
        ---
    get:
      description: Returns sensors attached to node
      summary: Find sensors by node id
      operationId: getSensorsFromNode
      produces:
      - application/json
      - text/html
      responses:
        '200':
          description: sensor response
          schema:
            type: array
            items:
              $ref: '#/definitions/Sensor'
        default:
          description: error payload
          schema:
            $ref: '#/definitions/ErrorModel'
    parameters:
    - name: id
      in: path
      description: ID of node to use
      required: true
      type: array
      items:
        type: string
    """


    if request.method == 'GET':
        results = Sensor.query.filter_by(node_id=nid).all()
        json_results = []

        for result in results:
            d = {'id': result.id,
                 'node_id': result.node_id,
                 'pin': result.pin,
                 'sensor_type': result.sensor_type}
            json_results.append(d)
        return json.jsonify(nodes = json_results)
    if request.method == 'POST':
        node_id = request.json.get('node_id')
        pin = request.json.get('pin')
        sensor_type = request.json.get('sensor_type')
        Node.query.filter(Sensor.id == id).update({'node_id': node_id, 'pin': pin,
                                                        'sensor_type': sensor_type})
        db.session.commit()
        return json.jsonify({'sensor': {'node_id': node_id, 'pin': pin,
                                                        'sensor_type': sensor_type}}), 201

