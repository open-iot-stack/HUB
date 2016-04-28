#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import thread
import threading
import hub
from chest import Chest
from flask import request
from flask import json
from flask import abort
from dealer import start_new_job
from dealer import PrinterCollector
from models import Printer, Job, File
import octopifunctions as octopi
from hub import app

@app.route('/printers', methods=['GET'])
def printers_list():
    """
        Printers List
        Returns a json of currently active printers
        ---
        tags:
          - printer
        responses:
          200:
            description: Returns a list of printers
        """

    log = hub.log
    listener = hub.printer_listeners
    internal = request.args.get("internal", "false")

    online = request.args.get('online_only', 'false')
    data = {"printers": []}
    printers = data.get("printers")
    for printer in Printer.get_printers():
        id = printer.id
        if online.lower() == 'true':
            with listener.lock:
                if listener.is_alive(id):
                    if internal.lower() == "true":
                        printers.append(printer.to_dict())
                    else:
                        printers.append(printer.to_web())
        else:
            if internal.lower() == "true":
                printers.append(printer.to_dict())
            else:
                printers.append(printer.to_web())
    return json.jsonify(data)

@app.route('/printers', methods=['POST'])
def add_printer():
    """
        Add Printer
        ---
        tags:
          - printer
        responses:
          200:
            description: Returns a printer
        """

    log = hub.log
    listener = hub.printer_listeners
    id   = int(request.form.get("id"))
    ip   = request.form.get("ip")
    port = int(request.form.get("port", 80))
    key  = request.form.get("key")
    printer = Printer.get_by_id(id)
    listener = hub.printer_listeners
    if printer:
        printer.update(ip=ip, port=port, key=key)
        if not listener.is_alive(id):
            t = PrinterCollector(id, hub.Webapi)
            t.start()
            listener.add_thread(id, t)
            log.log("Printer " + str(id) + " is now online.")
            return json.jsonify({'message': 'Printer ' + str(id)
                                            + ' is now online.'})
        if listener.is_alive(id):
            log.log("Printer " + str(id)
                    + " is already online but tried"
                    + " to activate again. Updated it's data")
            return json.jsonify({'message': 'Printer '
                                    + str(id)
                                    + ' was already online.'})
    else:
        #Add printer to database
        printer = Printer(id, key=key, ip=ip, port=port)
        t = PrinterCollector(id, hub.Webapi)
        t.start()
        listener.add_thread(id, t)
        return json.jsonify({'message': 'Printer ' + str(id)
                                + ' has been added and is online.'})



@app.route('/printers/<int:id>/<action>',methods=['POST'])
def print_action(id, action):
    """Post request to do a print action.
    :id: ID of the printer to command
    :action: Action to perform
    """
    """
        Print Action
                Add print action
        ---
        tags:
          - printer
        responses:
          200:
            description: Returns "(action) successfully sent to the printer."
        """

    if not hub.printer_listeners.is_alive(id):
        abort(400)
    printer = Printer.get_by_id(id)
    ip   = printer.ip
    port = printer.port
    key  = printer.key
    jobs = printer.jobs
    url = ip + ":" + str(port)
    log = hub.log

    #TODO make helper function for actions to respond the web api
    # with the actual success as the command. For now just spawn command
    # as new thread
    if action == "start":
        job = printer.current_job()
        if job:
            #TODO fix this to either unpause current job or start
            # a new job if applicable
            ext = job.file.name.rsplit('.', 1)[1]
            fpath = os.path.join(app.config['UPLOAD_FOLDER'],
                                    job.id+'.'+ext)
            thread.start_new_thread(start_new_job,(printer,job_id,fpath))
        else:
            abort(400)
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
            webid = request.form.get('id')
            job = Job.get_by_webid(webid)
            if not job:
                job = Job(int(webid))
                ext = f.filename.rsplit(".", 1)[1]
                name = str(job.id) + "." + ext
                fpath = os.path.join(app.config['UPLOAD_FOLDER'],name)
                f.save(fpath)
                file = File(f.filename, fpath)
                job.set_file(file)
                t = threading.Thread(target=upload_job, args=(id, job.id))
                t.start()

            #TODO Fix this to start a new job
            start = request.form.get('start', 'false')
            if start.lower() == "true":
                thread.start_new_thread(start_new_job,
                                        (printer_id,job.id,fpath))
        else:
            abort(400)
        # check if start is true, then make sure it is equal to true
    return json.jsonify({"message": action
                        + " successfully sent to the printer."})

@app.route('/printers/<int:id>', methods=['GET'])
def print_status(id):
    """
        Print Status
                Get printer status
        ---
        tags:
          - printer
        responses:
          200:
            description: TODO
        """
    #id = str(id)
    internal = request.args.get("internal", "false")
    if internal.lower() == "true":
        printer = Printer.get_by_id(id)
        return json.jsonify(printer.to_dict())
    printer = Printer.get_by_webid(id)
    #TODO return the actual data that's useful for the web api
    return json.jsonify(printer.to_web())

@app.route('/printers/<int:id>/jobs', methods=['GET'])
def jobs_list(id):
    """Returns a json of queued up jobs
    :returns: TODO
    """

    printer = Printer.get_by_webid(id)
    if printer:
        jobs = {
                "jobs": [ job.to_dict() for job in printer.jobs]
        }
        return json.jsonify(jobs)

@app.route('/printers/<int:id>/jobs', methods=['POST'])
def jobs_post(id):
    """Alternative way to add a job to a printer
    :id: webid of the printer you wish to add a job to
    """
    printer = Printer.get_by_webid(id)
    if printer == None:
        abort(404)
    id = printer.id
    f = request.files.get('file', None)
    if f:
        webid = request.form.get('id')
        job = Job.get_by_webid(webid)
        if not job:
            job = Job(int(webid))
            ext = f.filename.rsplit(".", 1)[1]
            name = str(job.id) + "." + ext
            fpath = os.path.join(app.config['UPLOAD_FOLDER'],name)
            f.save(fpath)
            file = File(f.filename, fpath)
            job.set_file(file)
            t = threading.Thread(target=upload_job, args=(id, job.id))
            t.start()

        #TODO Fix this to start a new job
        start = request.form.get('start', 'false')
        if start.lower() == "true":
            thread.start_new_thread(start_new_job,
                                    (printer_id,job.id,fpath))
    else:
        abort(400)
    return json.jsonify({"message": "Job " + str(webid)
                                    + " has been uploaded successfully"}),201

@app.route('/printers/<int:id>/jobs/current', methods=["GET"])
def jobs_current(id):
    """Returns a json of the current job
    :id: id of printer to get the job from
    :returns: current status of the job
    """
    """
        Jobs Current
                Get current job information
        ---
        tags:
          - printer
        responses:
          200:
            description: Returns current status of job
        """

    printer = Printer.get_by_id(id)
    if printer:
        job = printer.current_job()
        if job:
            return json.jsonify(job.to_dict())
        else:
            return json.jsonify({})
    abort(404)


@app.route('/jobs/<int:job_id>',
                                    methods=["GET","DELETE"])
def job_action(id, job_id):
    """Will either get or delete a job

    """
    if request.method == "GET":
        job = Job.get_by_id(job_id)
        if job:
            return json.jsonify(job.to_dict())
        else:
            abort(404)
    elif request.method == "DELETE":
        job = Job.get_by_id(job_id)
        if job:
            if job.position == 0:
                # TODO stop current job
                return {"NOT_IMPLEMENTED": "NOT_IMPLEMENTED"}
            else:
                printer = Printer.get_by_id(job.printer_id)
    pass
