#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
#from collections import OrderedDict
import os
from datetime import datetime as dt
from chest import Chest
from flask import request
from flask import json
from flask import abort
import octopifunctions as octopi

from hub import app

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
        prog["completion"] = progress.get("completion")
        prog["file_position"] = progress.get("filepos")
        prog["print_time"] = progress.get("printTime")
        prog["print_time_left"] = progress.get("printTimeLeft")
        progress = prog
    if not unix_date:
        unix_date = 0
    fdate = str(dt.fromtimestamp(unix_date).isoformat()[:-3])+'Z'
    njob["id"] = cjob.get("id", 0)
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

class Jobs(object):
    """Jobs is a class that will hold
    jobs for an individual printer
    """

    def __init__(self):
        """TODO: to be defined1. """

        self._jobs = []
        
    def add(self, fname, origin="remote"):
        """Add a job to the queue
        :fname: file to be added to the queue
        :returns: the id of the job
        """

        uuid = Uuid.generate()
        current_time   = dt.utcnow().isoformat()[:-3] + 'Z'
        st = os.stat(os.path.join(app.config["UPLOAD_FOLDER"], fname))
        fdate = str(dt.fromtimestamp(st.st_mtime).isoformat()[:-3])+'Z'
        self._jobs.append(
                    {
                      "id": uuid,
                      "created_at": current_time,
                      "updated_at": current_time,
                      "data": {
                        "status": "pending",
                        "file": {
                          "name": fname,
                          "origin": origin,
                          "size": st.st_size,
                          "date": fdate
                        }
                      }
                    })
        return uuid

    def remove(self, job_id):
        """Remove a job from the queue
        :job_id: id of job to be removed from the queue
        :returns: true if removed, false if unable or doesn't exist
        """

        job_id = str(job_id)
        if len(self._jobs):
            for job in self._jobs:
                if job.get("id") == job_id:
                    self._jobs.remove(job)
                    return True
        return False

    def list(self):
        """Return a list of dictionary jobs.
        Jobs will be in order of print queue
        :returns: List of jobs
        """

        return list(self._jobs)

    def next(self, remove=False):
        """Get the next job to be printed.
        :remove: will remove the data if set to True
        :returns: dictionary of job id and file, None if no jobs
        """

        if len(self._jobs) > 1:
            if remove:
                return self._jobs.pop(1)
            else:
                return self._jobs[1].copy()
        return None

    def current(self):
        """Returns a dictionary of the current job printing.
        Data in here is of local information, not from the
        printer
        :returns: dictionary of job
        """

        if len(self._jobs):
            return self._jobs[0].copy()
        return None

class Uuid(object):
    uuid = 0
    @staticmethod
    def generate():
        Uuid.uuid += 1
        return Uuid.uuid

if __name__ == "__main__":
    j = Jobs()
    t1 = j.add('test1')
    t2 = j.add('test2')
    t3 = j.add('test3')
    print str(j.list())
    t = j.next(remove=False)
    t["moose"] = "bit my sister"
    print json.dumps(str(j.list()))
    print str(j.next())
    j.remove(t2)
    print str(j.next(remove=False))
    print str(j.next())
