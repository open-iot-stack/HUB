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

class Jobs(object):
    """Jobs is a class that will hold
    jobs for an individual printer
    """

    def __init__(self, jobs = []):
        """TODO: to be defined1. """

        self._jobs = jobs

    def add(self, fname, printer_id, origin="remote"):
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
                      "printer": printer_id,
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
