#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import thread
from jobs import Jobs
from chest import Chest
from flask import request
from flask import json
from flask import abort
from dealer import job_data_collector
import octopifunctions as octopi
from hub import app

printers = Chest()

@app.route('/printers/list')
def printers_list():
    """Returns a json of currently active printers
    :returns: TODO
    """

    global printers
    data = {}
    with printers.lock:
        for uuid, printer in printers.data.iteritems():
            data[uuid] = {
                    "uuid": printer.get("uuid"),
                    "ip"  : printer.get("ip"),
                    "port": printer.get("port"),
                    "jobs": printer.get("jobs").list(),
                    "cjob": printer.get("cjob")
            }

    return json.jsonify(data)

@app.route('/printers/<int:uuid>/<action>',methods=['POST'])
def print_action(uuid, action):
    """Post request to do a print action. UUID must match a printer
    type in the config file
    """

    global printers
    uuid = str(uuid)
    with printers.lock:
        if not uuid in printers.data:
            abort(400)
        printer = printers.data.get(uuid)
        ip   = printer.get("ip")
        port = printer.get("port")
        key  = printer.get("key")
        jobs = printer.get("jobs")
        cjob = printer.get("cjob")

    url = "http://" + ip + ":" + port

    #TODO make helper function for actions to respond the web api
    # with the actual success as the command. For now just spawn command
    # as new thread
    if action == "start":
        #response = octopi.StartCommand(url, key)
        thread.start_new_thread(octopi.StartCommand, (url, key))
        thread.start_new_thread(job_data_collector, (printer,))
        pass

    elif action == "pause":
        #response = octopi.PauseUnpauseCommand(url, key)
        thread.start_new_thread(octopi.PauseUnpauseCommand, (url, key))
        pass

    elif action == "cancel":
        #response = octopi.CancelCommand(url, key)
        thread.start_new_thread(octopi.CancelCommand, (url, key))
        pass

    elif action == "upload":
        # get file from the post request
        # and place it in the upload folder
        #TODO make sure there is enough space on the device
        f = request.files.get('file', None)
        if f:
            fpath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(fpath)
            job_id = jobs.add(f.filename)
        start = request.args.get('start', None)
        # check if start isn't none, then make sure it is equal to true
        if start and start.lower() == "true":
            thread.start_new_thread(octopi.UploadFileAndPrint, (url, key, fpath))
            # TODO Make sure nothing else is printing
            # TODO remove job from jobs
            thread.start_new_thread(job_data_collector, (printer,))
            #TODO Handle starting the print job imediately
            pass
        pass
    return json.jsonify({"message": action
                        + " successfully sent to the printer."})

@app.route('/printers/<int:uuid>/status', methods=['GET'])
def print_status(uuid):
    global printers
    uuid = str(uuid)
    with printers.lock:
        if not uuid in printers.data:
            abort(400)
        printer = printers.data.get(uuid)
        ip   = printer.get("ip")
        port = printer.get("port")
        key  = printer.get("key")
        jobs = printer.get("jobs")
        cjob = printer.get("cjob")

    #url  = "http://" + ip + ":" + port

    #response = octopi.GetJobInfo(url, key)
    #TODO return the actual data that's useful for the web api
    return json.jsonify(cjob)


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

    uuid = str(payload.get("uuid"))
    ip   = payload.get("ip")
    port = str(payload.get("port", "80"))
    key  = str(payload.get("key", "0"))
    jobs = Jobs()
    cjob = {}

    with printers.lock:
        if uuid in printers.data:
            return json.jsonify({"message": uuid
                                + " was already activated."})
        printers.data[uuid] = {
                "uuid": uuid,
                "ip"  : ip,
                "port": port,
                "key" : key,
                "jobs": jobs,
                "cjob": cjob
        }
    #thread.start_new_thread(printer_data_collector,
    #                        (uuid, ip, port, key))

    return json.jsonify({"message": uuid + " has been activated."})

@app.route('/printers/<int:uuid>/jobs/list')
def jobs_list(uuid):
    """Returns a json of queued up jobs
    :returns: TODO
    """

    uuid = str(uuid)
    try:
        jobs = printers.data.get(uuid).get("jobs").list()
    except AttributeError:
        #TODO how to handle printer not existing
        jobs = []
    return json.jsonify(jobs)

@app.route('/printers/<int:uuid>/jobs/next')
def jobs_next(uuid):
    """Returns a json of the next job to be 
    processed by the printer
    """

    uuid = str(uuid)
    with printers.lock:
        if uuid in printers.data:
            job = printers.data.get(uuid).get("jobs").next(remove=False)
        else:
            #TODO if printer doesn't exists
            return json.jsonify({})
    if job:
        return json.jsonify(job)
    else:
        #TODO if job didn't exist
        return json.jsonify({})

@app.route('/printers/<int:uuid>/jobs/<int:job_id>',
                                    methods=["GET","DELETE"])
def job_action(uuid, job_id):
    """Will do the specified action on the job.
    """

    uuid   = str(uuid)

    if request.method == "GET":
        with printers.lock:
            try:
                printer = printers.data.get(uuid)
                # if current job, return current job data
                cjob = printer.get("cjob")
                if job_id == cjob.get("id"):
                    return json.jsonify(cjob.copy())
                # if not current job, find it in the jobs queue
                jobs = printer.get("jobs")
                for job in jobs.list():
                    if job_id == job.get("id"):
                        return json.jsonify(job.copy())
            except KeyError:
                log.log("ERROR: Jobs are corrupted")
        return json.jsonify({"ERROR": "ERROR"})
    elif request.method == "DELETE":
        with printers.lock:
            cjob = printer.get("cjob")
            if job_id == cjob.get("id"):
                # TODO stop current job
                return {"NOT_IMPLEMENTED": "NOT_IMPLEMENTED"}
    pass
