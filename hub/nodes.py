#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hub
from hub.chest import Chest
from flask import request, json, url_for, abort
from hub import app
from hub.dealer import NodeCollector, get_temp, get_gpio
from hub.database import db_session
from hub.models import Sensor, Node, Printer
from hub.tasks import Command
from hub import auth

NODE_ENDPOINT = '/nodes'
nodes = Chest()

@app.route(NODE_ENDPOINT, methods=['GET'])
@auth.login_required
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

    log = hub.log
    listener = hub.node_listeners
    internal = request.args.get("internal", "false")
    online   = request.args.get("online", "false")
    data = {"nodes": []}
    nodes = data.get("nodes")
    for node in Node.get_all():
        if internal.lower() != "true" and node.printer_id != None:
            continue
        if online.lower() == "true" and not listener.is_alive(node.id):
            continue
        nodes.append(node.to_web())
    return json.jsonify(data)

@app.route(NODE_ENDPOINT+'/<int:node_id>/sensors', methods=['GET'])
@auth.login_required
def node_sensors(node_id):
    """
        Get a list of sensors
        List's all sensors registered with node
        ---
        tags:
          - nodes
        parameters:
          - name: node_id
            in: path
            description: id of parent node
            required: true
            type: integer
        responses:
          200:
            description: Returns a list of sensors
        """

    results = Sensor.query.filter_by(node_id=node_id).all()
    json_results = []

    for result in results:
        d = {'id': result.id,
             'node_id': result.node_id,
             'sensor_type': result.sensor_type ,
             'freindly_id': result.friendly_id,
             'connection': result.state
            }
        if result.value:
            d['desired_state'] = json.loads(result.value)
        json_results.append(d)

    return json.jsonify(sensors = json_results)


@app.route(NODE_ENDPOINT+'/<int:node_id>', methods=['DELETE'])
@auth.login_required
def node_delete(node_id):
    """
        Delete a Node
        ---
        tags:
          - nodes
        parameters:
          - name: node_id
            in: path
            description: id of node
            required: true
            type: integer
        responses:
          200:
            description: Returns "Deleted"
        """
    Node.query.filter(Node.id == node_id).delete()
    db.session.commit()
    return json.jsonify({'message': 'Deleted'}), 201


@app.route('/sensors/<int:sensor_id>', methods=['GET'])
@auth.login_required
def get_sensor(sensor_id):
    """
        Get Sensor
        Get individual sensor information
        ---
        tags:
          - nodes
        parameters:
          - name: sensor_id
            in: path
            description: id of sensor
            required: true
            type: integer
        responses:
          200:
            description: Returns a Sensor
        """
    result = Sensor.query.filter_by(id=sensor_id).first()
    if result is None:
        abort(404)
    d = {'id': result.id,
         'node_id': result.node_id,
         'sensor_type': result.sensor_type ,
         'freindly_id': result.friendly_id,
         'state': result.state}
    if result.value:
        d.update(json.loads(result.value))
    return json.jsonify(sensor=d)


@app.route('/sensors/<int:sensor_id>', methods=['DELETE'])
@auth.login_required
def sensor_delete(sensor_id):
    """
        Delete a Sensor
        ---
        tags:
          - nodes
        parameters:
          - name: sensor_id
            in: path
            description: id of sensor
            required: true
            type: integer          
        responses:
          200:
            description: Returns "Deleted"
        """
    sensor = Sensor.get_by_webid(sensor_id)
    node   = Node.get_by_id(sensor.node_id)
    node.remove_sensor(sensor.id)
    return json.jsonify({'message': 'Deleted'}), 201