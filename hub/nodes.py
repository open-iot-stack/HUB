#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
import hub
from chest import Chest
from flask import request, json, url_for
from hub import app
from dealer import node_data_collector,get_temp,get_gpio
from database import db_session
from models import Sensor, Node

nodes = Chest()

@app.route('/nodes/<int:node_id>', methods=['GET'])
def node_data(node_id):
    """
        Get Node
        Get Individual Node
        ---
        tags:
          - nodes
        responses:
          200:
            description: Returns a Node
        """
    result = Node.query.filter_by(id=node_id).first()
    if result is None:
        abort(404)
    d = {'id': result.id,
         'ip': result.ip}
    return json.jsonify(node=d)


@app.route('/nodes/activate', methods=['GET'])
def activate_node(payload = None):
    """
        Activate Node
        Called by node to activate itself on the hub
        ---
        tags:
          - nodes
        responses:
          200:
            description: Returns a list of sensors
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
    """
        Get nodes
        List's all nodes activated on the hub
        ---
        tags:
          - nodes
        responses:
          200:
            description: Returns a list of nodes
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
    """
        Trigger Callback
        Called when node gpio triggered
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns node data
        """
    id   = int(request.args.get("id"))
    pin  = int(request.srgs.get("pin"))
    data = int(request.args.get("data"))

    d = {'id': id,
         'ip': pin,
         'data': data}
    return json.jsonify(d)


@app.route('/nodes/<int:node_id>/sensors', methods=['GET', 'POST'])
def node_sensors(node_id):
    """
        Get a list of sensors/Register Sensor
        List's all sensors registered with node
        Registers sensor on nodes
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns a list of sensors
        """


    if request.method == 'GET':
        results = Sensor.query.filter_by(node_id=node_id).all()
        json_results = []

        for result in results:
            d = {'id': result.id,
                 'node_id': result.node_id,
                 'pin': result.pin,
                 'sensor_type': result.sensor_type}
            json_results.append(d)
        return json.jsonify(sensors = json_results)
    if request.method == 'POST':
        pin = request.json.get('pin')
        sensor_type = request.json.get('sensor_type')
        sensor = Sensor(node_id, pin, sensor_type)
        db_session.add(sensor)
        db_session.commit()
        return json.jsonify({'sensor': {'node_id': node_id, 'pin': pin,
                                                        'sensor_type': sensor_type}}), 201

@app.route('/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    """
        Get Sensor
        Get individual sensor information
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns a Sensor
        """
    result = Sensor.query.filter_by(id=sensor_id).first()
    if result is None:
        abort(404)
    d = {'id': result.id,
         'node_id': result.node_id,
         'pin': result.pin,
         'sensor_type': result.sensor_type}
    return json.jsonify(sensor=d)


@app.route('/sensors/<int:sensor_id>/data', methods=['GET'])
def get_sensor_data(sensor_id):
    """
        Get Sensor Data
        Get individual sensor data
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns a data
        """
    result = Sensor.query.filter_by(id=sensor_id).first()
    if result is None:
        abort(404)
    node_result = Node.query.filter_by(id=result.node_id).first()
    if result is None:
        abort(404)

    if result.sensor_type == 'temp':
        temp, humidity = get_temp(node_result.ip, result.pin)
        d = {'temp': temp,
             'humi': humidity}
    else:
        data = get_gpio(node_result.ip, result.pin, result.sensor_type)
        d = {'data': data}

    return json.jsonify(data=d)