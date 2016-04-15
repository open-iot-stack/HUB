#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
#from collections import OrderedDict
from datetime import datetime as dt
from chest import Chest
from flask import request
from flask import json
from flask import abort
import octopifunctions as octopi
#from hub import app

def parse_jobstatus(job, cjob, status="NOT_IMPLEMENTED"):
    """Parses the passed in json file
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
    njob["id"] = cjob.get("id", 0)
    njob["created_at"] = cjob.get("created_at", dt)
    njob["updated_at"] = dt
    njob["data"] = {
        "status": status,
        "file": {
            "name": jf.get("name"),
            "origin": jf.get("origin"),
            "size": jf.get("size"),
            "date": dt.fromtimestamp(jf.get("date")).isoformat()[:-3]+'Z'
            },
        "estimated_print_time": job.get("estimatedPrintTime"),
        "filament": {
            "length": job.get("job").get("filament").get("length"),
            "volume": job.get("job").get("filament").get("volume")
            },
        "progress": {
            "completion": job.get("completion"),
            "file_position": job.get("filepos"),
            "print_time": job.get("printTime"),
            "print_time_left": job.get("printTimeLeft")
            }
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
                          "size": 0,
                          "date": 0
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

    def next(self, remove=True):
        """Get the next job to be printed.
        Removes job from queue
        :remove: will remove the data unless set to false
        :returns: dictionary of job id and file, None if no jobs
        """

        if len(self._jobs):
            if remove:
                return self._jobs.pop(0)
            else:
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
