#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from datetime import datetime as dt

def parse_printer_status(printer, state):
    """Parses the passed in dictionary.
    Set to match specifications
    :printer: printer dictionary of the printer status was retrieved from
    :printer_status: dictionary of status from the printer
    :returns: the information for the web api
    """
    id     = printer.id
    ip     = printer.ip
    port   = printer.port
    key    = printer.key
    friendly_id = state.get("friendly_id")
    manufacturer = state.get("manufacturer")
    model = state.get("model")
    description = state.get("description")
    num_jobs = printer.num_jobs()
    s = {
            "id": id,
            "friendly_id": friendly_id,
            "manufacturer": manufacturer,
            "model": model,
            "description": description,
            "num_jobs": num_jobs,
            "data": state
    }
    return s

def parse_job_status(job, status="NOT_IMPLEMENTED"):
    """Parses the passed in dictionary file
    Set to match specifications
    :returns: the information for the web api.
    """

    njob = {}
    #job = json.loads(json_job)
    jf = job.get("job").get("file")
    """if jf.get("data").get("name") != cjob.get("data").get("name"):
        log.log("ERROR: Current Job and New Job are not the same. "
                + "Current Job: " + str(cjob.get("data").get("name"))
                + " New Job: " + str(jf.get("data").get("name")))
    """
    name = jf.get("name")
    if name:
        id = name.split('.', 1)[0]
        fname = Job.get_by_id(id).file.name
    else:
        id = 0
        fname = None
    unix_date = jf.get("date")
    filament = job.get("job").get("filament")
    progress = job.get("progress")
    if progress:
        prog = {}
        prog["completion"] = progress.get("completion")
        prog["file_position"] = progress.get("filepos")
        prog["print_time"] = progress.get("printTime")
        prog["print_time_left"] = progress.get("printTimeLeft")
        progress = prog
    if not unix_date:
        unix_date = 0
    fdate = str(dt.fromtimestamp(unix_date).isoformat()[:-3])+'Z'
    njob["id"] = id
    njob["data"] = {
        "status": status,
        "file": {
            "name": fname,
            "origin": jf.get("origin"),
            "size": jf.get("size"),
            "date": fdate
            },
        "estimated_print_time": job.get("estimatedPrintTime"),
        "filament": filament,
        "progress": progress
        }
    return njob

