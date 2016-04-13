#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
from chest import Chest
from flask import request
from flask import json
from flask import abort
import octopifunctions as octopi
from hub import app

printers = Chest()

@app.route('/printers/list')
def printers_list():
    """Returns a json of currently active printers
    :returns: TODO
    """

    global printers
    return json.jsonify(printers.data)

@app.route('/printers/<int:uuid>/<action>',methods=['POST'])
def print_action(uuid, action):
    """Post request to do a print action. UUID must match a printer
    type in the config file
    """

    global printers
    uuid = str(uuid)
    with printers.lock:
        if not printers.data.has_key(uuid):
            abort(400)
        printer = printers.data.get(uuid)
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
    elif action == "upload":
        # get file from the post request
        # and place it in the upload folder
        #TODO make sure there is enough space on the device
        f = request.files.get('file', None)
        if f:
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        start = request.args.get('start', None)
        # check if start isn't none, then make sure it is equal to true
        if start and start.lower() == "true":
            #TODO Handle starting the print job imediately
            pass
        pass
    return json.jsonify({"message": action + " successfully sent to the printer."})

@app.route('/printers/<int:uuid>/status', methods=['GET'])
def print_status(uuid):
    global printers
    uuid = str(uuid)
    with printers.lock:
        if not printers.data.has_key(uuid):
            abort(400)
        printer = printers.data.get(uuid)
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
    if payload == None:
        str_payload = request.args.get("payload")
        payload     = json.loads(str_payload)

    uuid = payload.get("uuid")
    ip   = payload.get("ip")
    port = payload.get("port", "80")
    key  = payload.get("key", "0")

    with printers.lock:
        printers.data[uuid] = {
                "ip": ip,
                "port": port,
                "key": key
        }

    return json.jsonify({"message": uuid + " has been activated."})

