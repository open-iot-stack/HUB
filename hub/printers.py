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
from dealer import upload_and_print
from dealer import printer_data_collector
import octopifunctions as octopi
from hub import app

printers = Chest()

@app.route('/printers', methods=['GET', 'POST'])
def printers_list():
    """Returns a json of currently active printers
    :returns: TODO
    """

    global printers
    data = {}
    with printers.lock:
        for id, printer in printers.data.iteritems():
            data[id] = {
                    "id": printer.get("id"),
                    "ip"  : printer.get("ip"),
                    "port": printer.get("port"),
                    "jobs": printer.get("jobs").list(),
                    "cjob": printer.get("cjob"),
                    "status": printer.get("status")
            }

    return json.jsonify(data)

@app.route('/printers/<int:id>/<action>',methods=['POST'])
def print_action(id, action):
    """Post request to do a print action. UUID must match a printer
    type in the config file
    """

    global printers
    #id = str(id)
    with printers.lock:
        if not id in printers.data:
            abort(400)
        printer = printers.data.get(id)
        ip   = printer.get("ip")
        port = printer.get("port")
        key  = printer.get("key")
        jobs = printer.get("jobs")
        cjob = printer.get("cjob")

    url = ip + ":" + str(port)

    #TODO make helper function for actions to respond the web api
    # with the actual success as the command. For now just spawn command
    # as new thread
    if action == "start":
        job = jobs.current()
        if job:
            fpath = os.path.join(app.config['UPLOAD_FOLDER'],
                                    job["data"]["file"]["name"])
            job_id = job["id"]
        thread.start_new_thread(upload_and_print,(printer,job_id,fpath))
#        thread.start_new_thread(job_data_collector, (printer,))
        pass

    elif action == "pause":
        thread.start_new_thread(octopi.pause_unpause_command, (url, key))
        pass

    elif action == "cancel":
        thread.start_new_thread(octopi.cancel_command, (url, key))
        pass

    elif action == "upload":
        # get file from the post request
        # and place it in the upload folder
        #TODO make sure there is enough space on the device
        f = request.files.get('file', None)
        if f:
            fpath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(fpath)
            #TODO get job_id from request
            job_id = jobs.add(f.filename, id)
        else:
            abort(400)
        # check if start isn't none, then make sure it is equal to true
        start = request.args.get('start', 'false')
        if start.lower() == "true":
            thread.start_new_thread(upload_and_print,(printer,job_id,fpath))
            # TODO Make sure nothing else is printing
    return json.jsonify({"message": action
                        + " successfully sent to the printer."})

@app.route('/printers/<int:id>/status', methods=['GET'])
def print_status(id):

    #id = str(id)
    with printers.lock:
        if not id in printers.data:
            abort(400)
        printer = printers.data.get(id)
        ip   = printer.get("ip")
        port = printer.get("port")
        key  = printer.get("key")
        jobs = printer.get("jobs")
        cjob = printer.get("cjob")
        status = printer.get("status")

    #url  = "http://" + ip + ":" + str(port)

    #TODO return the actual data that's useful for the web api
    return json.jsonify(status.copy())


@app.route('/printers/activate', methods=['GET'])
def activate_printer():
    """API call to activate a printer on the hub.
    The printer should provide a parameter 'payload' in
    json format that contains it's IP address as "ip",
    id as "id", port as "port", and apikey as "key"
    :returns: TODO
    """

    global printers
    #TODO make into post method on /printers
    #TODO track thread that spawns for printer data
    id = int(request.args.get("id"))
    ip   = request.args.get("ip")
    port = int(request.args.get("port", 80))
    key  = request.args.get("key", "0")
    jobs = Jobs()
    cjob = {}
    status = {
        "id": id,
        "friendly_id": "NOT_IMPLEMENTED",
        "model": "NOT_IMPLEMENTED",
        "num_jobs": 0,
        "description": "NOT_IMPLEMENTED",
        "data" : {
            "state": {
                "text": "Operational",
                "flags": {
                    "operational": True,
                    "paused": False,
                    "printing": False,
                    "sd_ready": False,
                    "error": False,
                    "ready": False,
                    "closed_or_error": False
                }
            }
        }
    }
    with printers.lock:
        if id in printers.data:
            edit = False
            printer = printers.data.get(id)
            jobs = printer.get("jobs")
            cjob = printer.get("cjob")
            status = printer.get("status")
            if ip != printer.get("ip") or \
                   port != printer.get("port") or \
                   key != printer.get("key"):
                edit = True
            if not edit and status['data']['state']['text'] != "Offline":
                return json.jsonify({"message": str(id)
                                        + " was already activated."})
        printers.data[id] = {
                "id": id,
                "ip"  : ip,
                "port": port,
                "key" : key,
                "jobs": jobs,
                "cjob": cjob,
                "status": status
        }
        printer = printers.data[id]
        #TODO Move job_data_collector to only start when a job is running
    thread.start_new_thread(job_data_collector, (printer,))
    thread.start_new_thread(printer_data_collector, (printer,))

    return json.jsonify({"message": str(id) + " has been activated."})

@app.route('/printers/<int:id>/jobs/list')
def jobs_list(id):
    """Returns a json of queued up jobs
    :returns: TODO
    """

    try:
        jobs = printers.data.get(id).get("jobs").list()
    except AttributeError:
        abort(400)
    return json.jsonify(jobs)

@app.route('/printers/<int:id>/jobs/next')
def jobs_next(id):
    """Returns a json of the next job to be 
    processed by the printer
    """

    with printers.lock:
        if id in printers.data:
            job = printers.data.get(id).get("jobs").next(remove=False)
        else:
            #TODO if printer doesn't exists
            return json.jsonify({})
    if job:
        return json.jsonify(job)
    else:
        #TODO if job didn't exist
        return json.jsonify({})

@app.route('/printers/<int:id>/jobs/current', methods=["GET"])
def jobs_current(id):
    """Returns a json of the current job
    :id: id of printer to get the job from
    :returns: current status of the job
    """

    with printers.lock:
        if not id in printers.data:
            abort(400)
        cjob = printers.data[id]["cjob"].copy()
    return  json.jsonify(cjob)


@app.route('/printers/<int:id>/jobs/<int:job_id>',
                                    methods=["GET","DELETE"])
def job_action(id, job_id):
    """Will either add or delete a job

    """
    if request.method == "GET":
        with printers.lock:
            try:
                printer = printers.data.get(id)
                # if current job, return current job data
                if printer:
                    cjob = printer.get("cjob")
                    if job_id == cjob.get("id"):
                        return json.jsonify(cjob.copy())
                    # if not current job, find it in the jobs queue
                    jobs = printer.get("jobs")
                    for job in jobs.list():
                        if job_id == job.get("id"):
                            return json.jsonify(job.copy())
                else:
                    return json.jsonify({"ERROR": "Printer did not exist"})
            except KeyError:
                log.log("ERROR: Jobs are corrupted")
        return json.jsonify({"ERROR": "Could not find job"})
    elif request.method == "DELETE":
        with printers.lock:
            cjob = printer.get("cjob")
            if job_id == cjob.get("id"):
                # TODO stop current job
                return {"NOT_IMPLEMENTED": "NOT_IMPLEMENTED"}
    pass
