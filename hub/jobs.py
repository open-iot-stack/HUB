#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
from collections import OrderedDict
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

    def __init__(self):
        """TODO: to be defined1. """

        self._jobs = OrderedDict()
        
    def add(self, fname):
        """Add a job to the queue
        :fname: file to be added to the queue
        :returns: the id of the job
        """

        uuid = str(Uuid.generate())
        self._jobs[uuid] = {
                "file": fname
        }
        return uuid

    def remove(self, job_id):
        """Remove a job from the queue
        :job_id: job to be removed from the queue
        :returns: true if removed, false if unable or doesn't exist
        """

        try:
            job = self._jobs.pop(job_id)
        except KeyError:
            return False
        return True

    def list(self):
        """Return a dictionary list of jobs.
        Jobs will be in order of print queue
        :returns: OrderedDict of jobs
        """

        return self._jobs.copy()

    def next(self, remove=True):
        """Get the next job to be printed.
        Removes job from queue
        :remove: will remove the data unless set to false
        :returns: dictionary of job id and file, None if no jobs
        """

        if remove:
            jobs = self._jobs
        else:
            jobs = self._jobs.copy()
        try:
            job_id, job = jobs.popitem()
        except KeyError:
            return None
        return {job_id: job}

class Uuid(object):
    uuid = 0
    @staticmethod
    def generate():
        Uuid.uuid += 1
        return Uuid.uuid
