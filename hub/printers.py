#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import threading
import hub
from chest import Chest
from flask import request
from flask import json
from flask import abort
from dealer import PrinterCollector
from tasks import JobUploader, Command
from models import Printer, Job, File
from hub import app

@app.route('/printers', methods=['GET'])
def printers_list():
    """
        Printers List
        Returns a json of printers
        ---
        tags:
          - printer
        definitions:
          - schema:
              id: Web_Printer
              properties:
                id: 
                  type: integer
                  description: id of the printer on web api
                friendly_id: 
                  type: string
                  description: friendly_id of the printer
                manufacturer: 
                  type: string
                  description: manufacturer of the printer
                model: 
                  type: string
                  description: model of the printer
                num_jobs: 
                  type: integer
                  description: number of jobs the printer current has
                description: 
                  type: string
                  description: user description of the printer
                status: 
                  type: string
                  description: status of the printer
        produces:
        - application/json
        responses:
          200:
            description: Returns a list of printers
            schema:
              properties:
                printers:
                  type: array
                  items:
                    $ref: "#/definitions/Web_Printer"
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
        Adds or updates printer
        ---
        tags:
          - printer
        parameters:
          - in: body
            name: Printer
            description: Printer object to be added/activated
            required: true
            schema:
              id: Post_Printer
              required:
                - id
                - ip
                - key
              properties:
                ip:
                  type: string
                  description: ip address of connecting printer
                key:
                  type: string
                  description: api key for octopi
                id:
                  type: integer
                  description: uid of the printer activating
                port:
                  type: integer
                  description: port number to communicate on
        responses:
          201:
            description: Returns 201 created
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
                                + ' has been added and is online.'}),201



@app.route('/printers/<int:id>/commands',methods=['POST'])
def print_action(id):
    """
        Print Action
        Add print action
        ---
        tags:
          - printer
        parameters:
          - in: path
            required: true
            name: id
            description: ID of printer
            type: integer
          - in: body
            name: Command
            description: Command to be excecuted
            required: true
            schema:
              required:
                - id
                - type
              properties:
                id:
                  type: integer
                  description: id of the command
                type:
                  type: string
                  description: type of command to send [start, pause, cancel, next]
        responses:
          200:
            description: Returns "(action) successfully sent to the printer."

        """
    printer = Printer.get_by_webid(id)
    if printer == None:
        abort(404)
    id   = printer.id
    ip   = printer.ip
    port = printer.port
    key  = printer.key
    jobs = printer.jobs
    url = ip + ":" + str(port)
    log = hub.log
    data = request.get_json()
    command_id = data.get("id")
    action = data.get("type")

    if action == "start":
        t = Command(id, log, "start",
                hub.Webapi, command_id=command_id)
    elif action == "pause":
        t = Command(id, log, "pause",
                hub.Webapi, command_id=command_id)
    elif action == "cancel":
        t = Command(id, log, "cancel",
                hub.Webapi, command_id=command_id)
    elif action == "next":
        t = Command(id, log, "next",
                hub.Webapi, command_id=command_id)
    t.start()
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
        parameters:
          - in: path
            description: ID of the printer
            required: true
            type: integer
            name: id
        responses:
          200:
            description: returns printer information
            schema:
              $ref: "#/definitions/Web_Printer"

    """
    internal = request.args.get("internal", "false")
    if internal.lower() == "true":
        printer = Printer.get_by_id(id)
        if printer == None:
            abort(404)
        return json.jsonify(printer.to_dict())
    printer = Printer.get_by_webid(id)
    if printer == None:
        abort(404)
    return json.jsonify(printer.to_web())

@app.route('/printers/<int:id>/jobs', methods=['GET'])
def jobs_list(id):
    """
        Jobs List
        Get list of queued jobs
        ---
        tags:
          - printer
        parameters:
          - in: path
            description: ID of the printer
            required: true
            type: integer
            name: id
        definitions:
          - schema:
              id: Web_Job
              required:
                - id
              properties:
                id:
                  type: integer
                  description: ID of the printer
                data:
                  schema:
                    id: Web_Job_Data
                    properties:
                      estimated_print_time:
                        type: integer
                        description: size of the job in bytes
                      status:
                        type: string
                        description: status of the job
                      file:
                        schema:
                          id: Web_Job_File
                          properties:
                            name:
                              type: string
                              description: name of the file
                            origin:
                              type: string
                              description: origin of the file
                            size:
                              type: integer
                              description: size of the file in bytes
                            date:
                              type: string
                              description: date the file was created
        responses:
          200:
            description: returns json of queued jobs
            schema:
              properties:
                jobs:
                  type: array
                  items:
                    $ref: "#/definitions/Web_Job"

    """
    printer = Printer.get_by_webid(id)
    if printer:
        jobs = {
                "jobs": [ job.to_web(None) for job in printer.jobs]
        }
        return json.jsonify(jobs)
    abort(404)

@app.route('/printers/<int:id>/jobs', methods=['POST'])
def jobs_post(id):
    """
        Add a Job
        Add job to printer
        ---
        tags:
          - printer
        parameters:
          - in: path
            description: ID of the printer
            required: true
            type: integer
            name: id
          - in: body
            description: Job to add to the printer
            required: true
            name: Job
            schema:
              $ref: "#/definitions/Web_Job"
        responses:
          201:
            description: returns "(job) has been uploaded successfully"
          400:
            description: no file was provided
          404:
            description: printer isn't found
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
        elif job.file == None:
            ext = f.filename.rsplit(".", 1)[1]
            name = str(job.id) + "." + ext
            fpath = os.path.join(app.config['UPLOAD_FOLDER'],name)
            f.save(fpath)
            file = File(f.filename, fpath)
            job.set_file(file)
        printer = Printer.get_by_id(id)
        printer.add_job(job)
        t = threading.Thread(target=hub.Webapi.patch_job,
                            args=(job.to_web(None),))
        t.start()
        if printer.current_job().id == job.id:
            t = Command(printer.id, hub.log, "start",
                        hub.Webapi)
            t.start()
    else:
        abort(400)
    return json.jsonify({"message": "Job " + str(webid)
                            + " has been uploaded successfully"}),201

@app.route('/printers/<int:id>/jobs/current', methods=["GET"])
def jobs_current(id):
    """
        Jobs Current
        Get current job information
        ---
        tags:
          - printer
        parameters:
          - in: path
            description: ID of the printer
            required: true
            type: integer
            name: id
        responses:
          200:
            description: Returns current status of job
            schema:
              $ref: "#/definitions/Web_Job"
        """

    printer = Printer.get_by_id(id)
    if printer:
        job = printer.current_job()
        if job:
            return json.jsonify(job.to_web(None))
        else:
            return json.jsonify({})
    abort(404)


@app.route('/jobs/<int:job_id>', methods=["GET"])
def get_job(job_id):
    """
        Job Action
        Get current job information
        ---
        tags:
          - printer
        parameters:
          - in: path
            description: ID of the job
            required: true
            type: integer
            name: id
        responses:
          200:
            description: Returns current status of job
            schema:
              $ref: "#/definitions/Web_Job"
        """

    job = Job.get_by_webid(job_id)
    if job:
        return json.jsonify(job.to_dict())
    else:
        abort(404)

@app.route('/jobs/<int:job_id>', methods=["DELETE"])
def delete_job(job_id):
    """
        Delete Job Action
        Stops and Deletes Job
        ---
        tags:
          - printer
        parameters:
          - in: path
            type: integer
            name: id
            description: ID of the Job
            required: true
        responses:
          200:
            description: TODO
        """

    job = Job.get_by_webid(job_id)
    if job:
        printer = Printer.get_by_id(job.printer_id)
        if printer != None:
            if job.position == 0:
                if printer.state("cancelled"):
                    printer.cancel_job()
                    payload = printer.to_web()
                    hub.Webapi.patch_printer(payload)
            else:
                printer.remove_job(job_id)
        if job.state("errored"):
            payload = job.to_web(None)
            hub.Webapi.patch_job(payload)
    return json.jsonify({"message": "Job " + str(job_id)
                                    + " has been deleted"}),200
