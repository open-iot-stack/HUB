#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from datetime import datetime as dt

def parse_printer_status(printer, printer_state):
    """Parses the passed in dictionary.
    Set to match specifications
    :printer: printer dictionary of the printer status was retrieved from
    :printer_status: dictionary of status from the printer
    :returns: the information for the web api
    """
    uuid = printer.get("uuid")
    jobs = printer.get("jobs")
    status = printer.get("status")
    friendly_id = status.get("friendly_id")
    manufacturer = status.get("manufacturer")
    model = status.get("model")
    description = status.get("description")
    num_jobs = len(jobs.list())
    s = {
            "id": uuid,
            "friendly_id": friendly_id,
            "manufacturer": manufacturer,
            "model": model,
            "description": description,
            "num_jobs": num_jobs,
            "data": printer_state
    }
    return s

def parse_job_status(job, cjob, status="NOT_IMPLEMENTED"):
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
    njob["id"] = cjob.get("id", 0)
    njob["printer"] = cjob.get("printer", 0)
    njob["created_at"] = cjob.get("created_at", fdate)
    njob["updated_at"] = fdate
    njob["data"] = {
        "status": status,
        "file": {
            "name": jf.get("name"),
            "origin": jf.get("origin"),
            "size": jf.get("size"),
            "date": fdate
            },
        "estimated_print_time": job.get("estimatedPrintTime"),
        "filament": filament,
        "progress": progress
        }
    return njob

