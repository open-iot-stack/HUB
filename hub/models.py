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

    def __repr__(self):
        return "<File(name='%s')>" % (self.name)

class Job(Base):
    __tablename__="job"

    id         = Column(Integer, primary_key=True)
    position      = Column(Integer)
    status     = Column(String)
    file       = relationship("File", back_populates="job", uselist=False)
    printer    = relationship("Printer", back_populates="jobs", uselist=False)
    printer_id = Column(Integer, ForeignKey("printer.id"))

    @staticmethod
    def get_by_id(id):
        """Returns a job based on id
        :id: ID of job to be found
        :returns: Job if id is found, None if didn't exist

        """
        job =\
            db_session.query(Job).filter(Job.id == id).one_or_none()
        return job

    def __init__(self, id,  file, status="queued"):
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

    def state(self, state):
        """Set the status of the current job
        :state: State of the print job, must be in
            ["processing", "slicing", "printing",
            "completed", "paused", "errored", "queued"]:
        :returns: boolean of success

        """
        if state in ["processing", "slicing", "printing", "completed", "paused",
                "errored", "queued"]:
            self.status = state
            db_session.commit()
            return True
        return False

    def __repr__(self):
        return "<Job(id='%d', position='%d', status='%s', file='%s')>" %\
        (self.id, self.position, self.status, self.file)

class Printer(Base):
    __tablename__="printer"

    id   = Column(Integer, primary_key=True)
    status = Column(String)
    jobs = relationship("Job", order_by=Job.position, back_populates="printer",
                                collection_class=ordering_list("position"))
    ip   = None
    port = 0

    @staticmethod
    def get_by_id(id):
        """Returns a printer based on id
        :id: ID of printer to be found
        :returns: Printer if id is found, None if didn't exist

        """
        printer =\
            db_session.query(Printer).filter(Printer.id == id).one_or_none()
        return printer

    def __init__(self, id, ip="0.0.0.0", port=80, status="Offline"):
        """Creates a new Printer, adds to database. If printer exists
        or params aren't formatted correctly, will throw and exception
        :id: id of the printer
        :status: State of the printer, must be in
            ["Operational", "Paused", "Printing", "Offline",
            "SD Ready", "Error", "Ready", "Closed on Error"]

        """
        self.id   = id
        self.ip   = ip
        self.port = port
        if not status in ["Operational", "Paused", "Printing", "Offline",
                            "SD Ready", "Error", "Ready", "Closed on Error"]:
            status = "Offline"
        self.status = status
        db_session.add(self)
        db_session.commit()

    def update(self, ip=None, port=None, status=None):
        """Update data on printer
        :ip: IP address to set to
        :port: Port to set to
        :status: Status to set to
        :returns: Boolean of sucess

        """
        if status:
            if status in ["Operational", "Paused", "Printing", "Offline",
                            "SD Ready", "Error", "Ready", "Closed on Error"]:
                self.status = status
                db_session.commit()
            else:
                return False
        if ip:
            self.ip = ip
        if port:
            self.port = port
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
        return True

    def state(self, state):
        """Sets the status of the printer
        :state: state of the printer to set. Will return false if not in
                ["Operational", "Paused", "Printing", "Offline",
                "SD Ready", "Error", "Ready", "Closed on Error"]
        :returns: boolean of success

        """
        if state in ["Operational", "Paused", "Printing", "Offline",
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
