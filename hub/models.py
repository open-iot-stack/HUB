#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from database import Base, db_session

class PrinterExists(Exception):
    pass
class JobExists(Exception):
    pass

class File(Base):
    __tablename__="file"

    id = Column(Integer, primary_key=True)
    name   = Column(String)
    origin = Column(String)
    size   = Column(Integer)
    date   = Column(String)
    job    = relationship("Job", back_populates="file", uselist=False)
    job_id = Column(Integer, ForeignKey("job.id"))

    def __init__(self, name):
        self.name = name
        db_session.add(self)
        db_session.commit()

    def to_dict(self):
        """Returns dictionary representation of a file
        :returns: TODO

        """
        d = {
                "name": self.name
        }
        return d

    def __repr__(self):
        return "<File(name='%s')>" % (self.name)

class Job(Base):
    __tablename__="job"

    id         = Column(Integer, primary_key=True)
    webid      = Column(Integer, unique=True)
    position   = Column(Integer)
    status     = Column(String)
    file       = relationship("File", back_populates="job",
                                uselist=False)
    printer_id = Column(Integer, ForeignKey("printer.id"))

    @staticmethod
    def get_by_id(id):
        """Returns a job based on id
        :id: ID of job to be found
        :returns: Job if id is found, None if didn't exist

        """
        db_session.remove()
        job =\
            db_session.query(Job).filter(Job.id == id).one_or_none()
        return job

    @staticmethod
    def get_by_webid(webid):
        """Returns a job based on webid
        :webid: WebID of job to be found
        :returns: Job if webid is found, None if didn't exist

        """
        db_session.remove()
        job =\
            db_session.query(Job).\
                filter(Job.webid == webid).one_or_none()
        return job

    def __init__(self, id,  file, webid=None, status="queued"):
        """Create a job object. A file object should be created first.
        :id: id of the job
        :file: file that the job refers to
        :status: status of the job. Leave blank by default
        :position: position within the list. Leave blank by default
        :returns: nothing

        """
        self.id = id
        self.status = status
        self.file = file
        #atm the webid and id should be the same
        if webid:
            self.webid = webid
        else:
            self.webid = id
        db_session.add(self)
        db_session.commit()

    def state(self, state):
        """Set the status of the current job
        :state: State of the print job, must be in
            ["processing", "slicing", "printing",
            "completed", "paused", "errored", "queued"]:
        :returns: boolean of success

        """
        if state in ["processing", "slicing", "printing",
                        "completed", "paused", "errored",
                        "queued"]:
            self.status = state
            db_session.commit()
            return True
        return False

    def set_webid(self, webid):
        """Sets the webid of the job. ATM is the same as ID
        and set at creation
        :webid: ID used by the web api
        :returns: boolean of success

        """
        self.webid = webid
        db_session.commit()
        return True

    def to_web(self, job):
        """Properly formats data to be sent to the web api 
        
        """

        jf = job.get("job").get("file")
        if jf.get('name') == None:
            return None
        id = self.webid
        if jf.get('name').split('.',1)[0] != str(id):
            return None
        fname = self.file.name
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
            "status": self.status,
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

    def to_dict(self):
        """Returns a dictionary representation of the Job
        :returns: dictionary of job

        """
        d = {
                "id": self.id,
                "file": self.file.to_dict(),
                "status": self.status
        }
        return d

    def __repr__(self):
        return "<Job(id='%d', status='%s', file='%s')>" %\
        (self.id, self.status, self.file)

class Printer(Base):
    __tablename__="printer"

    id   = Column(Integer, primary_key=True)
    webid = Column(Integer, unique=True)
    status = Column(String)
    jobs = relationship("Job", order_by=Job.position,
            back_populates="printer",
            collection_class=ordering_list("position"))
    key  = Column(String)
    ip   = Column(String)
    port = Column(Integer)
    friendly_id = Column(String)
    manufacturer = Column(String)
    model = Column(String)
    description = Column(String)

    @staticmethod
    def get_by_id(id):
        """Returns a printer based on id
        :id: ID of printer to be found
        :returns: Printer if id is found, None if didn't exist

        """
        db_session.remove()
        printer =\
            db_session.query(Printer).\
                filter(Printer.id == id).one_or_none()
        return printer

    @staticmethod
    def get_by_webid(webid):
        """Returns a printer based on webid
        :webid: ID that the web interface uses
        :returns: Printer if webid is found, None if didn't exist

        """
        db_session.remove()
        printer =\
            db_session.query(Printer).\
                filter(Printer.webid == webid).one_or_none()
        return printer

    @staticmethod
    def get_printers():
        """Retrieve all printers in the database
        :returns: TODO

        """
        db_session.remove()
        l = []
        for printer in db_session.query(Printer):
            l.append(printer)
        return l

    def __init__(self, id, key=None, ip=None, port=80, status="Paused",
                friendly_id=None, manufacturer=None, model=None
                , description=None, webid=None):
        """Creates a new Printer, adds to database. If printer exists
        or params aren't formatted correctly, will throw and exception
        :id: id of the printer
        :status: State of the printer, must be in
            ["Operational", "Paused", "Printing",
            "SD Ready", "Error", "Ready", "Closed on Error"]

        """
        self.id           = id
        self.webid        = webid
        self.key          = key
        self.ip           = ip
        self.port         = port
        self.model        = model
        self.friendly_id  = friendly_id
        self.description  = description
        self.manufacturer = manufacturer

        if not status in ["Operational", "Paused", "Printing",
                            "SD Ready", "Error", "Ready", "Closed on Error"]:
            status = "Offline"
        self.status = status
        db_session.add(self)
        db_session.commit()

    def update(self, ip=None, port=None, status=None, key=None):
        """Update data on printer
        :ip: IP address to set to
        :port: Port to set to
        :status: Status to set to. Must be in 
            ["Operational", "Paused", "Printing",
            "SD Ready", "Error", "Ready", "Closed on Error"]:
        :returns: Boolean of sucess

        """
        if status:
            if status in ["Operational", "Paused", "Printing",
                            "SD Ready", "Error", "Ready",
                            "Closed on Error"]:
                self.status = status
            else:
                return False
        if key:
            self.key = key
        if ip:
            self.ip = ip
        if port:
            self.port = port
        db_session.commit()
        return True

    def set_webid(self, webid):
        """Sets the web id for the printer
        :webid: ID that web gave back to communicate
        :returns: boolean of success.
        """
        self.webid = webid
        db_session.commit()
        return True

    def is_online(self):
        """Check if printer is online
        :returns: True if online, false if Offline or Errored

        """
        if self.status in ["Offline", "Error", "Closed on Error"]:
            return False
        return True

    def set_ip(self, ip, port=None):
        """Set the ip for a given printer
        :ip: IP to set on the printer
        :port: port to set to
        :returns: boolean of success

        """
        self.ip = ip
        if port:
            self.port = port
        db_session.commit()
        return True

    def state(self, state):
        """Sets the status of the printer
        :state: state of the printer to set. Will return false if not in
                ["Operational", "Paused", "Printing",
                "SD Ready", "Error", "Ready", "Closed on Error"]
        :returns: boolean of success

        """
        if state in ["Operational", "Paused", "Printing",
                        "SD Ready", "Error", "Ready", "Closed on Error"]:
            self.status = state
            db_session.commit()
            return True
        return False

    def add_job(self, job, position=-1):
        """Add a job to the printer. This will set it to the position.
        If another job is in that location, it bumps it back. Cannot add 
        to front of queue
        :job: Adds job to the the printer queue
        :position: Position to be added to the queue. If -1, appends
        :returns: Boolean of success

        """
        if position == 0:
            return False
        for j in self.jobs:
            if j.id == job.id:
                return False
        if position == -1:
            self.jobs.append(job)
            db_session.commit()
            print self
            return True
        if position >= len(self.jobs):
            self.jobs.append(job)
            db_session.commit()
            return True
        else:
            self.jobs.insert(position, job)
            db_session.commit()
            return True

    def remove_job(self, job_id):
        """Removes the job from the job queue
        Fails if job is the current job
        :job_id: id of the job to be removed
        :returns: boolean of success
        """

        db_session.remove()
        job = db_session.query(Job).filter(Job.id == job_id).one_or_none()
        if job:
            if job.position == 0:
                return False
            self.jobs.remove(job)
            db_session.commit()
            return True
        return False

    def complete_job(self, job_id):
        """Does the proper handling of a job completing.
        :job_id: id of the job that completed
        :returns: boolean of success

        """
        pass

    def next_job(self):
        """Returns the next job to be printed
        :returns: next job in the queue. returns None if no job

        """
        if len(self.jobs) > 1:
            return self.jobs[1]
        return None

    def current_job(self):
        """Returns the current job of the printer
        :returns: current job of the printer, if no job returns None

        """
        if self.jobs:
            return self.jobs[0]
        return None

    def num_jobs(self):
        """Returns the number of jobs the printer has
        :returns: Number of jobs

        """
        return len(self.jobs)

    def to_dict(self):
        """Returns a dictionary object that represents the printer
        :returns: dictionary
        
        """
        d = {
                "id": self.id,
                "ip": self.ip,
                "port": self.port,
                "jobs": [j.to_dict() for j in self.jobs],
                "status": self.status,
                "num_jobs": self.num_jobs(),
                "friendly_id": self.friendly_id,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "description": self.description
        }
        return d

    def to_web(self, state):
        """Properly formats data to be sent to the web api

        :state: TODO
        :returns: TODO

        """
        d = {
                "id": self.webid,
                "friendly_id": self.id,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "num_jobs": self.num_jobs(),
                "description": self.description,
                "data": state
        }
        return d

    def __repr__(self):
        return "<Printer(id='%d', ip='%s', port='%d', status='%s' jobs='%s')>"\
                % (self.id, str(self.ip), int(self.port),
                        self.status, self.jobs)


class Node(Base):
    __tablename__="nodes"

    id = Column(Integer, primary_key=True)
    ip = Column(String)

    def __init__(self, id, ip):
        self.id = id
        self.ip = ip

    def __repr__(self):
        return "<Node='%d' ip='%s')>"\
                % (self.id, self.ip)


class Sensor(Base):
    __tablename__="sensors"

    id   = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    pin  = Column(Integer)
    sensor_type = Column(String)


    def __init__(self, node_id, pin, sensor_type):
        self.node_id = node_id
        self.pin = pin
        self.sensor_type = sensor_type

    def __repr__(self):
        return "<Sensor='%d' node_id='%d', pin='%d', sensor_type='%s')>"\
                % (self.node_id, self.pin, self.type)
