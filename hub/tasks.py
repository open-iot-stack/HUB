#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import threading
import requests
import octopifunctions as octopi
from time import sleep
from models import Printer, Node, Job

class Command(threading.Thread):

    """Sends a command to a printer as a task"""

    @staticmethod
    def start(id, log, webapi=None, command_id=None):
        """Creates a Command object that will send a start signal,
        or if paused, will unpause the job
        :id: id of the printer to start
        :log: Log object to log errors
        :returns: a started Command Object that is running as a thread
            
        """
        c = Command(id, "start", log,
                        webapi=webapi, command_id=command_id)
        c.start()
        return c

    @staticmethod
    def pause(id, log, webapi=None, command_id=None):
        """Creates a Command object that will send a pause signal
        :id: id of printer to pause
        :log: Log object to log errors
        :returns: a started Command object that is running as a thread

        """
        c = Command(id, "pause", log,
                        webapi=webapi, command_id=command_id)
        c.start()
        return c

    @staticmethod
    def cancel(id, log, webapi=None, command_id=None):
        """Creates a Command object that will send a cancel signal
        :id: id of printer to cancel
        :log: Log object to log errors
        :returns: a started Command object that is running as a thread

        """
        c = Command(id, "cancel", log,
                        webapi=webapi, command_id=command_id)
        c.start()
        return c

    def __init__(self, id, command, log, webapi=None, command_id=None):
        """Create a new thread object to issue a command to a printer

        :id: TODO
        :command: TODO

        """
        threading.Thread.__init__(self)

        self.id         = id
        self.command    = command
        self.success    = False
        self.log        = log
        self.command_id = command_id
        self.webapi     = webapi

    def run(self):
        id      = self.id
        log     = self.log
        job_id  = self.job_id
        command = self.command
        loc     = octopi.local
        printer = Printer.get_by_id(id)
        ip      = printer.ip
        port    = printer.port
        key     = printer.key
        status  = printer.status
        url     = ip + ":" + port

        if command == "start":
            if status == "paused":
                i = 0
                r = octopi.toggle_pause(url, key)
                while r == None or i < 10:
                    sleep(1)
                    r = octopi.toggle_pause(url, key)
                    i += 1
                if r and r.status_code == 204:
                    self.success = True
            elif status == "ready":
                cjob = printer.current_job()
                i = 0
                r = octopi.select_and_print(cjob.remote_name)
                while r == None or i < 10:
                    sleep(1)
                    r = octopi.select_and_print(cjob.remote_name)
                    i += 1
                if r and r.status_code == 204:
                    self.success = True
        elif command == "pause":
            if status == "printing":
                i = 0
                r = octopi.toggle_pause(url, key)
                while r == None or i < 10:
                    sleep(1)
                    r = octopi.toggle_pause(url, key)
                    i += 1
                if r and r.status_code == 204:
                    self.success = True
        elif command == "cancel":
            if status in ["printing", "paused"]:
                if printer.state("cancelled"):
                    i = 0
                    r = octopi.cancel(url, key)
                    while r == None or i < 10:
                        sleep(1)
                        r = octopi.cancel(url, key)
                        i += 1
                    if r and r.status_code == 204:
                        self.success = True
        if self.command_id != None and self.webapi != None:
            d = {
                "id": self.command_id,
                "type": command
            }
            if self.success == True:
                d['status'] = 'executed'
            else:
                d['status'] = 'errored'
            i = 0
            while self.webapi.callback_command(d) or i < 10:
                i += 1
        return 0

class JobUploader(threading.Thread):

    """JobUploader will upload a job to the printer"""

    def __init__(self, id, job_id, log):
        """Create a new thread object for upload jobs to a printer
        :id: printer id to upload file to
        :job_id: job id of job to be uploaded

        """
        threading.Thread.__init__(self)

        self.id      = id
        self.job_id  = job_id
        self.success = False
        self.log     = log
        
    def run(self):
        """Function that will upload a new file, slice it if needed,
        and delete stl files from the octopi. Should be used whenever
        a new job is uploaded to the hub
        :returns: boolean of success

        """
        id      = self.id
        log     = self.log
        job_id  = self.job_id
        loc     = octopi.local
        printer = Printer.get_by_id(id)
        ip      = printer.ip
        port    = printer.port
        key     = printer.key
        job     = Job.get_by_id(job_id)
        log.log("Starting job upload to " + str(id)
                + " for job " + str(job.id))
        fpath = job.file.path
        job.state("processing")
        url = ip + ":" + str(port)
        r = octopi.upload_file(url, key, fpath, loc)
        if r == None:
            log.log("ERROR: Did not have a response from " + str(id)
                    + ". File upload canceled for " + fpath + ".")
            self.success = False
            return False
        if r.status_code != 201:
            log.log("ERROR: Could not upload file " + fpath
                    + ". Return code from printer " + str(r.status_code))
            return False
        data = r.json()
        fname = data['files']['local']['name']
        ext = get_extension(fname)
        if ext in ['stl']:
            job.state("slicing")
            r = octopi.slice(url, key, fname, loc)
            if r == None:
                log.log("ERROR: Did not have a response from " + str(id)
                        + ". Job upload canceled for job "
                        + str(job_id) + ".")
                self.success = False
                return False
            if r.status_code != 202:
                log.log("ERROR: Job start failed for " + str(job_id)
                        + ". Return code from printer "
                        + str(r.status_code))
                self.success = False
                return False
            j = r.json()
            rname = j.get('name')
            #TODO somehow delete stl file as well
            r = octopi.get_one_file_info(url, key, rname, loc)
            while r == None or r.status_code != 200:
                #This is really fucking hacky
                log.log("Could not retrieve file info for " + str(job.id))
                sleep(10)
                r = octopi.get_one_file_info(url, key, rname, loc)

            j = r.json()
            print_time = j.get("gcodeAnalysis").get("estimatedPrintTime")
            job.set_print_time(print_time)
            job.set_remote_name(rname)
            r = octopi.delete_file(url, key, fname, loc)
            while r == None:
                sleep(10)
                r = octopi.delete_file(url, key, fname, loc)
        elif ext in ['gcode', 'gco']:
            r = octopi.get_one_file_info(url, key, fname, loc)
            while r == None or r.status_code != 200:
                #This is really fucking hacky
                log.log("Could not retrieve file info for " + str(job.id))
                sleep(10)
                r = octopi.get_one_file_info(url, key, fname, loc)

            j = r.json()
            print_time = j.get("gcodeAnalysis").get("estimatedPrintTime")
            job.set_print_time(print_time)
            job.set_remote_name(fname)
        else:
            self.success = False
            return False
        printer = Printer.get_by_id(id)
        printer.add_job(job)
        if printer.current_job().id == job.id:
            Command.start(printer.id, log)
        self.success = True
        return True

def get_extension(name):
    """Returns the extension of a file.
    :path: path of file to get the extension of
    :returns: file extension

    """
    ext = name.rsplit('.', 1)[1]
    return ext
    
