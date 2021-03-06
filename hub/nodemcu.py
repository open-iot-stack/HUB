#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import hub
from hub.chest import Chest
from flask import request, json, url_for, abort
from hub import app
from hub.dealer import NodeCollector, get_temp, get_gpio
from hub.database import db_session
from hub.models import Sensor, Node, Printer
from hub.tasks import Command
from hub import auth

NODE_MCU_ENDPOINT = '/nodes/nodemcu'

@app.route(NODE_MCU_ENDPOINT+'/activate', methods=['GET'])
@auth.login_required
def activate_node(payload = None):
    """
        Activate Node
        Called by node to activate itself on the hub
        ---
        tags:
          - nodemcu
        responses:
          200:
            description: Returns a list of sensors
        """

    global nodes
    id   = int(request.args.get("id"))
    ip   = str(request.args.get("ip"))
    port = int(request.args.get("port", 80))
    log = hub.log
    listener = hub.node_listeners

    node = Node.get_by_id(id)
    if node:
        node.update(ip=ip)
        if not listener.is_alive(id):
            t = NodeCollector(id, hub.Webapi, hub.log)
            t.start()
            listener.add_thread(id, t)
            log.log("Node " + str(id) + " is now online.")
            return json.jsonify({'message': "Node " + str(id)
                                            + " is now online."}),201
        if listener.is_alive(id):
            log.log("Node " + str(id)
                    + " is already online but tried"
                    + " to activate again, Updated it's data")
            return json.jsonify({'message': "Node " + str(id)
                                            + " was already online"}),201
    else:
        node = Node(id, ip)
        updates = {"nodes": []}
        node_updates = updates.get("nodes")
        for node in Node.get_all(fresh=True):
            if node.printer_id == None:
                node_updates.append(node.id)
        t = threading.Thread(target=hub.Webapi.update_nodes,args=updates)
        t.start()
        return json.jsonify({"message": str(id) + " has been activated."}),201

@app.route(NODE_MCU_ENDPOINT+'/trigger/callback', methods=['POST'])
@auth.login_required
def nodes_trigger_callback():
    """
        Trigger Callback
        Called when node gpio triggered
        ---
        tags:
          - nodemcu
        responses:
          200:
            description: Returns node data
        """
    payload = request.get_json()
    id   = int(payload.get("id"))
    data = payload.get("data")
    node = Node.get_by_id(id)
    if node.printer_id:
        printer = Printer.get_by_id(node.printer_id)
        if printer.status in ["completed", "cancelled"]:
            t = Command(printer.id, hub.log, "clear", hub.Webapi)
        else:
            t = Command(printer.id, hub.log, "cancel", hub.Webapi)
        t.start()
        for sensor in node.sensors:
            if sensor.sensor_type == "LED":
                url = sensor.led_on()
                t = threading.Thread(target=requests.get,
                                     args=(url,))
                t.start()
        #r = requests.get(url, timeout=10)
    d = {'id': id,
         'data': data}
    return json.jsonify(d)

@app.route(NODE_MCU_ENDPOINT+'/<int:node_id>/sensors', methods=['POST'])
@auth.login_required
def node_add_sensors(node_id):
    """
        Add a Sensor
        Registers sensor on nodes
        ---
        tags:
          - nodemcu
        definitions:
          - schema:
              id: Post_Sensor
              required:
                - id
                - type
              properties:
                id:
                  type: integer
                  description: id of the sensor
                type:
                  type: string
                  description: type of sensor
                  enum: ['door','temperature','trigger','led']
        parameters:
          - in: body
            name: Sensor
            description: Sensor object to be added to the hub
            schema:
              $ref: '#/definitions/Post_Sensor'

        responses:
          201:
            description: Returns the information received about the sensor
        """
    payload = request.get_json()
    webid  = payload.get("id")
    sensor = Sensor.get_by_webid(webid)
    if sensor:
        abort(409)
    sensor_type = payload.get('type')
    if sensor_type == "door":
        sensor_type = "DOOR"
    elif sensor_type == "temperature":
        sensor_type = "TEMP"
    elif sensor_type == "humidity":
        sensor_type = "HUMI"
    elif sensor_type == "trigger":
        sensor_type = "TRIG"
    elif sensor_type == "led":
        sensor_type = "LED"
    else:
        abort(400)
    sensor = Sensor(node_id, sensor_type, webid=webid)
    return json.jsonify({'sensor': {'node_id': node_id, 'sensor_type': sensor_type}}), 201


@app.route(NODE_MCU_ENDPOINT+'/sensors/<int:sensor_id>/data', methods=['GET'])
@auth.login_required
def get_sensor_data(sensor_id):
    """
        Get Sensor Data
        Get individual sensor data
        ---
        tags:
          - nodemcu
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
        temp, humidity = get_temp(node_result.ip, result.value)
        d = {'temp': temp,
             'humi': humidity}
    else:
        data = get_gpio(node_result.ip, result.value, result.sensor_type)
        d = {'data': data}

    return json.jsonify(data=d)
