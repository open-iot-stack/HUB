#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import thread
from hub.models import Job, File, Printer
from hub.database import db_session


class Printers(object):
    """Represents the currently active printers"""

    def __init__(self):
        """TODO: to be defined1. """
        self._lock = thread.allocate_lock()
        pass
        
    def add(self, printer):
        """Add a printer and it's list of jobs to the database, if printer
        exists, will add the jobs to it's job queue.
        :returns: false if couldn't add
        """
        uuid = printer.get("uuid")
        jobs = printer.get("jobs")
        cjob = printer.get("cjob")

        with self._lock:
            p = db_session.query(Printer).filter_by(uuid=uuid).first()
            if p:
                if p.uuid != uuid:
                    p.uuid = uuid
                if jobs:
                    #TODO check differences, atm just makes a new list
                    p.jobs = []
                    for i in range(len(jobs.list())):
                        job = jobs.list()[i]
                        data = job.get("data")
                        status = None
                        file = None
                        if data:
                            file = data.get("file")
                            status = data.get("status")
                            f = File(name=file.get("name"),origin=file.get("origin"),
                                    size=file.get("size"),date=file.get("date"))
                        j = Job(uuid=job.get("id"),created_at=job.get("created_at"),
                                updated_at=job.get("updated_at"),status=status,
                                order=i)
                        if file:
                            j.file = [f]
                        p.jobs += [j]

                if cjob and len(cjob):
                    job = cjob
                    data = job.get("data")
                    status = None
                    file = None
                    if data:
                        file = data.get("file")
                        status = data.get("status")
                        f = File(name=file.get("name"),origin=file.get("origin"),
                                size=file.get("size"),date=file.get("date"))
                    j = Job(uuid=job.get("id"),created_at=job.get("created_at"),
                            updated_at=job.get("updated_at"),status=status,
                            order=0)
                    if file:
                        j.file = [f]
                    p.cjob = [j]
                db_session.commit()
                    
                #TODO Check difference and adjust those values
            else:
                #TODO Add uuid to database and 
                p = Printer(uuid=uuid)
                if jobs:
                    for i in range(len(jobs.list())):
                        job = jobs.list()[i]
                        data = job.get("data")
                        status = None
                        file = None
                        if data:
                            file = data.get("file")
                            status = data.get("status")
                            f = File(name=file.get("name"),origin=file.get("origin"),
                                    size=file.get("size"),date=file.get("date"))
                        j = Job(uuid=job.get("id"),created_at=job.get("created_at"),
                                updated_at=job.get("updated_at"),status=status,
                                order=i)
                        if file:
                            j.file = [f]
                        p.jobs += [j]

                if cjob and len(cjob):
                    job = cjob
                    data = job.get("data")
                    status = None
                    file = None
                    if data:
                        file = data.get("file")
                        status = data.get("status")
                        f = File(name=file.get("name"),origin=file.get("origin"),
                                size=file.get("size"),date=file.get("date"))
                    j = Job(uuid=job.get("id"),created_at=job.get("created_at"),
                            updated_at=job.get("updated_at"),status=status,
                            order=0)
                    if file:
                        j.file = [f]
                    p.cjob = [j]

                db_session.add(p)
                db_session.commit()

    def get(self, uuid):
        """Gets a printer dictionary for a given uuid
        :returns: false if printer doesn't exist
        """

        p = db_session.query(Printer).filter(Printer.uuid==uuid).first()
        ret = {
                "uuid": None,
                "jobs": [],
                "cjob": None
        }
        ret["uuid"] = p.uuid

        for job in p.jobs:
            file = None
            if job.file:
                file = {
                    "name":   job.file.name,
                    "origin": job.file.origin,
                    "size": job.file.size,
                    "date": job.file.date
                }
            ret["jobs"].append({
                "id" :        job.uuid,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
                "order"     : job.order,
                "data" : {
                    "status": job.status,
                    "file": file
                }
            })

        for job in p.cjob:
            file = None
            if job.file:
                file = {
                    "name":   job.file.name,
                    "origin": job.file.origin,
                    "size": job.file.size,
                    "date": job.file.date
                }
            ret["cjob"] = {
                "id":         job.uuid,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
                "order"     : job.order,
                "data" : {
                    "status": job.status,
                    "file"  : file
                }
            }
        return ret

    def delete(self, uuid):
        """Deletes the printer from the database
        :returns: false if printer doesn't exist
        """
        pass
