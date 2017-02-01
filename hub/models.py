#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime as dt
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from hub.database import Base, db_session
from flask import json

class PrinterExists(Exception):
    pass
class JobExists(Exception):
    pass

class File(Base):
    __tablename__="files"

    id = Column(Integer, primary_key=True)
    name   = Column(String)
    origin = Column(String)
    size   = Column(Integer)
    date   = Column(Integer)
    path   = Column(String)
    ext    = Column(String)
    job_id = Column(Integer, ForeignKey("jobs.id"))

    def __init__(self, name, path, ext=None,
                    size=0, date=0, origin="remote"):
        self.name = name
        self.path = path
        self.origin = origin
        if ext == None:
            ext = name.rsplit(".",1)[1]
        if date == 0:
            date = int(time.time())
        if size == 0:
            size = os.stat(path).st_size
        self.ext = ext
        self.date = date
        self.size = size
        db_session.add(self)
        db_session.commit()

    def to_web(self):
        """Returns a dictionary to be sent to the web api
        :returns: TODO

        """
        fdate = str(dt.fromtimestamp(self.date).isoformat()[:-3])+'Z'
        d = {
                "name": self.name,
                "path": self.path,
                "origin": self.origin,
                "size": self.size,
                "date": fdate
        }
        return d

    def to_dict(self):
        """Returns dictionary representation of a file
        :returns: TODO

        """
        d = {
                "name": self.name,
                "origin": self.origin,
                "size": self.size,
                "date": self.date
        }
        return d

    def __repr__(self):
        return "<File(name='%s')>" % (self.name)

class Job(Base):
    __tablename__="jobs"

    id           = Column(Integer, primary_key=True)
    webid        = Column(Integer, unique=True)
    position     = Column(Integer)
    status       = Column(String)
    printer_id   = Column(Integer, ForeignKey("printers.id"))
    remote_name  = Column(String)
    filament     = Column(String)
    progress     = Column(String)
    file         = relationship("File", uselist=False)
    estimated_print_time = Column(String)

    @staticmethod
    def get_by_id(id, fresh=False):
        """Returns a job based on id
        :id: ID of job to be found
        :returns: Job if id is found, None if didn't exist

        """
        if fresh == True:
            db_session.remove()
        job =\
            db_session.query(Job).filter(Job.id == id).first()
        return job

    @staticmethod
    def get_by_webid(webid, fresh=False):
        """Returns a job based on webid
        :webid: WebID of job to be found
        :returns: Job if webid is found, None if didn't exist

        """
        if fresh == True:
            db_session.remove()
        job =\
            db_session.query(Job).\
                filter(Job.webid == webid).first()
        return job

    def __init__(self, webid, status="queued"):
        """Create a job object. A file object should be created first.
        :id: id of the job
        :file: file that the job refers to
        :status: status of the job. Leave blank by default
        :position: position within the list. Leave blank by default
        :returns: nothing

        """
        self.webid = webid
        self.status = status
        self.file = None
        db_session.add(self)
        db_session.commit()

    def set_file(self, file):
        """Set a file for the job. Fails if job already holds a file
        :file: File object to be set as the file
        :returns: boolean of success

        """
        if self.file != None:
            return False
        self.file = file
        db_session.commit()
        return True
        pass

    def state(self, state):
        """Set the status of the current job
        :state: State of the print job, must be in
            ["processing", "slicing", "printing",
            "completed", "paused", "errored", "queued"]:
        :returns: boolean of success

        """
        if state == self.status:
            return True
        if self.status == "cancelled":
            return False
        if state in ["processing", "slicing", "printing",
                        "completed", "paused", "errored",
                        "queued", "cancelled"]:
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

    def set_remote_name(self, remote_name):
        """Sets the remote name of the job.
        :remote_name: name that is on the octopi
        :returns: boolean of success

        """
        self.remote_name = remote_name
        db_session.commit()
        return True

    def set_meta(self, job):
        jf = job.get("job").get("file")
        if jf.get('name') == None:
            return False
        filament = job.get("job").get("filament")
        if filament:
            filament = json.dumps(filament)
        progress = job.get("progress")
        estimated_print_time = job.get("job").get("estimatedPrintTime")
        if progress:
            prog = {}
            completion = progress.get("completion")
            if completion == None:
                completion = 0
            prog["completion"] = int(completion)
            prog["file_position"] = progress.get("filepos")
            prog["print_time"] = progress.get("printTime")
            prog["print_time_left"] = progress.get("printTimeLeft")
            progress = json.dumps(prog)
        self.filament = str(filament)
        self.progress = str(progress)
        self.estimated_print_time = str(estimated_print_time)
        db_session.commit()
        return True

    def to_web(self):
        """Properly formats data to be sent to the web api

        """
        try:
            progress = json.loads(self.progress)
        except:
            progress = None
        try:
            filament = json.loads(self.filament)
        except:
            filament = None
        njob = {
            "id": self.webid,
            "data": {
                "status": self.status,
                "file": self.file.to_web(),
                "estimated_print_time": self.estimated_print_time,
                "filament": filament,
                "progress": progress
            }
        }
        return njob

    def to_dict(self):
        """Returns a dictionary representation of the Job
        :returns: dictionary of job

        """
        d = {
                "id": self.id,
                "webid": self.webid,
                "file": self.file.to_dict(),
                "status": self.status
        }
        return d

    def __repr__(self):
        return "<Job(id='%d', status='%s', file='%s')>" %\
        (self.id, self.status, self.file)

class Printer(Base):
    __tablename__="printers"

    id           = Column(Integer, primary_key=True)
    webid        = Column(Integer, unique=True)
    status       = Column(String)
    prev_status  = Column(String)
    jobs         = relationship("Job", order_by=Job.position,
                     collection_class=ordering_list("position"))
    key          = Column(String)
    ip           = Column(String)
    port         = Column(Integer)
    friendly_id  = Column(String)
    manufacturer = Column(String)
    model        = Column(String)
    description  = Column(String)
    blackbox     = relationship("Node", uselist=False)

    @staticmethod
    def get_by_id(id, fresh=False):
        """Returns a printer based on id
        :id: ID of printer to be found
        :returns: Printer if id is found, None if didn't exist

        """
        if fresh == True:
            db_session.remove()
        printer =\
            db_session.query(Printer).\
                filter(Printer.id == id).first()
        return printer

    @staticmethod
    def get_by_webid(webid, fresh=False):
        """Returns a printer based on webid
        :webid: ID that the web interface uses
        :returns: Printer if webid is found, None if didn't exist

        """
        if fresh == True:
            db_session.remove()
        printer =\
            db_session.query(Printer).\
                filter(Printer.webid == webid).first()
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

    @staticmethod
    def get_all(fresh=False):
        if fresh == True:
            db_session.remove()
        printers = db_session.query(Printer).all()
        return printers

    def __init__(self, id, box, key=None, ip=None, port=80, status="offline",
                friendly_id=None, manufacturer=None, model=None
                , description=None, webid=None):
        """Creates a new Printer, adds to database. If printer exists
        or params aren't formatted correctly, will throw and exception
        :id: id of the printer
        :status: State of the printer, must be in
            ["ready", "paused", "printing", "errored",
            "offline", "cancelled", "completed"]

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
        node = Node.get_by_id(box)
        if node == None:
            node = Node(box, None)
        power = Sensor(box, 2, "POWER")
        trigger = Sensor(box, 3 , "TRIG")
        led     = Sensor(box, 4, "LED")
        self.blackbox = node
        if not status in ["ready", "paused", "printing", "errored",
                            "offline", "cancelled", "completed"]:
            status = "offline"
        self.status = status
        db_session.add(self)
        db_session.commit()

    def update(self, box=None, ip=None, port=None, status=None, key=None):
        """Update data on printer
        :ip: IP address to set to
        :port: Port to set to
        :status: Status to set to. Must be in
            ["ready", "paused", "printing", "errored",
            "offline", "cancelled", "completed"]:
        :returns: Boolean of sucess

        """
        if status:
            ret = self.state(status)
            if ret == False:
                return False
        if key:
            self.key = key
        if ip:
            self.ip = ip
        if port:
            self.port = port
        if box:
            if box != self.blackbox.id:
                node = Node.get_by_id(box)
                if node == None:
                    node = Node(box, None)
                power = Sensor(box, 2, "POWER")
                trigger = Sensor(box, 3 , "TRIG")
                led     = Sensor(box, 4, "LED")
                self.blackbox = node
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
        if self.status in ["errored", "offline"]:
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

    def state_from_octopi(self, state):
        """Sets the state of the printer based on output from
        the octopi.

        :state: TODO
        :returns: TODO

        """
        if state:
            text  = state.get("state").get("text")
            flags = state.get("state").get("flags")
        else:
            return False
        if flags.get("error") == True:
            return self.state("error")
        elif flags.get("closedOrError") == True:
            return self.state("error")
        elif flags.get("printing") == True:
            return self.state("printing")
        elif flags.get("paused") == True:
            return self.state("paused")
        elif flags.get("ready") == True:
            return self.state("ready")
        elif flags.get("sdReady") == True:
            return self.state("ready")
        return False

    def state(self, state):
        """Sets the status of the printer
        :state: Status to set to. Must be in
            ["ready", "paused", "printing", "errored",
            "offline", "cancelled", "completed"]:
        :returns: boolean of success

        """
        if self.status == state:
            return True
        # if setting to offline, store the previous state
        if state == "offline":
            if self.status != "offline":
                if self.status in ["printing", "paused"]:
                    self.status = "cancelled"
                self.prev_status = self.status
                self.status = "offline"
                db_session.commit()
            return True
        #If the printer was offline, load the prev status
        # and try setting the state. Makes sure cancelled and completed
        # still stay in that mode
        if self.status == "offline":
            self.status = self.prev_status
            db_session.commit()
            return self.state(state)

        if self.status == "completed":
            return False
        elif self.status == "cancelled":
            return False
        if state in ["ready", "paused", "printing", "errored",
                        "completed", "cancelled"]:
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
            job.state("queued")
            self.jobs.append(job)
            db_session.commit()
            return True
        if position >= len(self.jobs):
            job.state("queued")
            self.jobs.append(job)
            db_session.commit()
            return True
        else:
            job.state("queued")
            self.jobs.insert(position, job)
            db_session.commit()
            return True

    def remove_job(self, job_id):
        """Removes the job from the job queue
        Fails if job is the current job
        :job_id: id of the job to be removed
        :returns: boolean of success

        """
        job = Job.get_by_id(job_id)
        if job.printer_id != self.id:
            return False
        if job:
            if job.position == 0:
                if self.status == "ready" and job.status == "errored":
                    self.jobs.remove(job)
                    db_session.commit()
                    return True
                return False
            self.jobs.remove(job)
            db_session.commit()
            return True
        return False

    def cancel_job(self):
        """Does the proper handling of a job canceling.
        :returns: boolean of success

        """
        job = self.current_job()
        if job == None:
            return False
        if self.status != "cancelled":
            return False
        self.jobs.remove(job)
        self.status = "ready"
        db_session.commit()
        return True

    def complete_job(self):
        """Does the proper handling of a job completing.
        :returns: boolean of success

        """
        job = self.current_job()
        if job == None:
            return False
        if self.status != "completed":
            return False
        self.jobs.remove(job)
        self.status = "ready"
        db_session.commit()
        return True


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
                "webid": self.webid,
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

    def first_web(self):
        """Properly formats data to be sent to the web api for registration

        :state: TODO
        :returns: TODO

        """
        d = {
            "id": self.webid,
            "friendly_id": "Printer " + str(self.id),
            "status": self.status
        }
        return d

    def to_web(self):
        """Properly formats printer to be sent to the web api

        """
        d = {
            "id": self.webid,
            "status": self.status
        }
        return d

    def __repr__(self):
        return "<Printer(id='%d', ip='%s', port='%d', status='%s' jobs='%s')>"\
                % (self.id, str(self.ip), int(self.port),
                        self.status, self.jobs)


class Node(Base):
    __tablename__="nodes"

    id = Column(Integer, primary_key=True)
    webid = Column(Integer, unique=True)
    friendly_id = Column(String)
    ip = Column(String)
    sensors = relationship("Sensor")
    printer_id = Column(Integer, ForeignKey("printers.id"))

    @staticmethod
    def get_by_id(id, fresh=False):
        """Returns a node based on id
        :id: ID of node to be found
        :returns: Node if id is found, None if didn't exist

        """
        if fresh == True:
            db_session.remove()
        node =\
            db_session.query(Node).\
                filter(Node.id == id).first()
        return node

    @staticmethod
    def get_all(fresh=False):
        """Returns all the nodes in the database
        """
        if fresh == True:
            db_session.remove()
        nodes = db_session.query(Node).all()
        return nodes

    def __init__(self, id, ip, friendly_id=None):
        self.id = id
        self.ip = ip
        self.friendly_id = friendly_id
        db_session.add(self)
        db_session.commit()

    def remove_sensor(self, sensor_id):
        sensor = Sensor.get_by_id(sensor_id)
        if sensor.node_id != self.id:
            return False
        self.sensors.remove(sensor)
        db_session.commit()
        return True

    def update(self, ip=None):
        if ip:
            self.ip = ip
        db_session.commit()
        return True

    def set_webid(self, webid):
        self.webid = webid
        db_session.commit()
        return True

    def to_web(self):
        d = {
            "id": self.id
        }
        return d

    def __repr__(self):
        return "<Node='%d' ip='%s')>"\
                % (self.id, self.ip)

class Account(Base):
    __tablename__="accounts"
    account_name = Column(String, primary_key=True)
    web_token = Column(String)
    web_refresh_token = Column(String)
    token_endpoint = Column(String)

    def __init__(self, account_name, web_token, web_refresh_token,
                    token_endpoint):
        self.account_name = account_name
        self.web_token = web_token
        self.web_refresh_token = web_refresh_token
        self.token_endpoint = token_endpoint
        db_session.add(self)
        db_session.commit()

    @staticmethod
    def get_all(fresh=False):
        """Returns all the nodes in the database
        """
        if fresh == True:
            db_session.remove()
        accounts = db_session.query(Account).all()
        return accounts

    @staticmethod
    def get_by_name(name, fresh=False):
        if fresh == True:
            db_session.remove()
        account =\
            db_session.query(Account).\
                filter(Account.account_name == name).first()
        return account

    def update(self, web_token=None, web_refresh_token=None):
        if web_token and web_refresh_token:
            self.web_token = web_token
            self.web_refresh_token = web_refresh_token
        db_session.commit()
        return True

    def to_dict(self):
        d = {
            "account_name": self.account_name,
            "web_token": self.web_token,
            "web_refresh_token": self.web_refresh_token,
            "token_endpoint": self.token_endpoint,
            }
        return d

class Sensor(Base):
    __tablename__="sensors"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    sensor_type = Column(String)
    webid = Column(Integer, unique=True)
    value = Column(String)
    raw = Column(String)
    friendly_id = Column(String)
    state = Column(String)

    def __init__(self, node_id, sensor_type, webid=None, value=None, raw=None, friendly_id=None, state='DISCONNECTED'):
        self.node_id = node_id
        self.sensor_type = sensor_type
        self.webid = webid
        self.value
        self.raw
        self.friendly_id
        self.state
        db_session.add(self)
        db_session.commit()

    @staticmethod
    def get_by_webid(id, fresh=False):
        if fresh == True:
            db_session.remove()
        sensor =\
            db_session.query(Sensor).\
                filter(Sensor.webid == id).first()
        return sensor

    @staticmethod
    def get_by_id(id, fresh=False):
        if fresh == True:
            db_session.remove()
        sensor =\
            db_session.query(Sensor).\
                filter(Sensor.id == id).first()
        return sensor

    def update(self):
            db_session.commit()

    def to_dict(self):
        d = {
            "id": self.id,
            "type": self.sensor_type,
            "webid": self.webid,
            "value": self.value,
            "raw": self.raw,
            "friendly_id": self.friendly_id,
            "state": self.state
            }
        return d

    # def led_on(self):
    #     """Makes a URL for making a sensor of type LED to stay on.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "LED":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip = node.ip
    #     value  = self.value
    #     url = "http://" + ip + "/gpio/" + str(pin) + "/high"
    #     return url
    #
    # def led_off(self):
    #     """Makes a URL for making a sensor of type LED to stay off.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "LED":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip = node.ip
    #     pin  = self.pin
    #     url = "http://" + ip + "/gpio/" + str(pin) + "/low"
    #     return url
    #
    # def led_flash(self, freq=None):
    #     """Makes a URL for making a sensor of type LED to flash.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "LED":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip = node.ip
    #     pin  = self.pin
    #     url = "http://" + ip + "/gpio/" + str(pin) + "/pwm"
    #     return url
    #
    # def power_on(self):
    #     """Makes a URL for making a sensor of type POWER to power on.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "POWER":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip   = node.ip
    #     pin  = self.pin
    #     url  = "http://" + ip + "/gpio/" + str(pin) + "/high"
    #     return url
    #
    # def power_off(self):
    #     """Makes a URL for making a sensor of type POWER to power off.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "POWER":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip   = node.ip
    #     pin  = self.pin
    #     url  = "http://" + ip + "/gpio/" + str(pin) + "/low"
    #     return url
    #
    # def door_status(self):
    #     """Makes a URL for getting the data from a type DOOR sensor.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "DOOR":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip   = node.ip
    #     pin  = self.pin
    #     url = "http://" + ip + "/gpio/" + str(pin) + "/input"
    #     return url
    #
    # def temp_status(self):
    #     """Makes a URL for getting the data from a type TEMP sensor.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "TEMP":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip   = node.ip
    #     pin  = self.pin
    #     url = "http://" + ip + "/gpio/" + str(pin) + "/temp"
    #     return url
    #
    # def humi_status(self):
    #     """Makes a URL for getting the data from a type HUMI sensor.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "HUMI":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip   = node.ip
    #     pin  = self.pin
    #     url = "http://" + ip + "/gpio/" + str(pin) + "/humi"
    #     return url
    #
    # def trigger(self):
    #     """Makes a URL for setting a sensor of type TRIG to enter
    #     triggered mode.
    #     returns None if wrong sensor type
    #     """
    #     if self.sensor_type != "TRIG":
    #         return None
    #     node = Node.get_by_id(self.node_id)
    #     ip   = node.ip
    #     pin  = self.pin
    #     url = "http://" + ip + "/gpio/" + str(pin) + "/trig"
    #     return url
    #
    # def get_url(self):
    #     """Makes a URL for getting data from a sensor.
    #     URL is based on sensor_type. If sensor_type is not a
    #     data collecting sensor, returns None
    #     """
    #     if self.sensor_type == "TRIG":
    #         return self.trigger()
    #     elif self.sensor_type == "TEMP":
    #         return self.temp_status()
    #     elif self.sensor_type == "DOOR":
    #         return self.door_status()
    #     elif self.sensor_type == "HUMI":
    #         return self.humi_status()
    #     return None
    #
    # def set_humi(self, data):
    #     if self.sensor_type != "HUMI":
    #         return False
    #     self.value = str(data.get("humi"))
    #     db_session.commit()
    #     return True
    #
    # def set_temp(self, data):
    #     if self.sensor_type != "TEMP":
    #         return False
    #     self.value = str((float(data.get("temp")) * 9/5.0) + 32.0)
    #     db_session.commit()
    #     return True
    #
    # def set_door(self, data):
    #     if self.sensor_type != "DOOR":
    #         return False
    #     self.value = str(data.get("data"))
    #     db_session.commit()
    #     return True
    #
    # def set_value(self, data):
    #     if self.sensor_type == "HUMI":
    #         return self.set_humi(data)
    #     if self.sensor_type == "TEMP":
    #         return self.set_temp(data)
    #     if self.sensor_type == "DOOR":
    #         return self.set_door(data)
    #
    # def humi_to_web(self):
    #     if self.sensor_type != "HUMI":
    #         return None
    #     d = {
    #         "id": self.webid,
    #         "value": str(self.value)
    #     }
    #     return d
    #
    # def temp_to_web(self):
    #     """Parses the output of a sensor of type TEMP to work
    #     with the web api.
    #     returns a list of data to be sent, empty list if wrong type
    #     """
    #     if self.sensor_type != "TEMP":
    #         return None
    #     d = {
    #         "id": self.webid,
    #         "value": str(self.value)
    #     }
    #     return d
    #
    # def door_to_web(self):
    #     """Parses the output of a sensor of type DOOR to work
    #     with the web api.
    #     returns a list of data to be sent, empty list if wrong type
    #     """
    #     if self.sensor_type != "DOOR":
    #         return None
    #     d = {
    #         "id": self.webid,
    #         "value": int(self.value)
    #     }
    #     return d
    #
    # def to_web(self):
    #     """Parses the output of a sensor's data to work with
    #     the web api. Parsing is based on sensor type
    #     returns a list of data to send to webapi
    #     """
    #     if self.sensor_type == "DOOR":
    #         return self.door_to_web()
    #     elif self.sensor_type == "TEMP":
    #         return self.temp_to_web()
    #     elif self.sensor_type == "HUMI":
    #         return self.humi_to_web()
    #     return self.to_dict()
