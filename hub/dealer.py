#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hub
import threading
import requests
import webapi
import octopifunctions as octopi
from time import sleep
from flask import json
from models import Printer, Node, Job
from hub import app

class PrinterCollector(threading.Thread):

    """Printer Collector will continue to grab """

    def __init__(self, printer_id, webapi):
        """TODO: to be defined1. """
        threading.Thread.__init__(self)
        self.printer_id = printer_id
        printer = Printer.get_by_id(printer_id)
        status = printer.status
        self.stopped = False
        self.webapi = webapi
        self.cancelled = status == "cancelled"
        self.completed = status == "completed"
        self.lock = threading.Lock()

    def cancel(self):
        self.cancelled = True

    def complete(self):
        self.completed = True

    def status(self, status):
        self.status = status

    def run(self):
        id = self.printer_id
        webapi = self.webapi
        printer = Printer.get_by_id(id, fresh=True)
        # loop until the printer has a webid,
        # otherwise we can't update
        while printer.webid == None:
            webid = webapi.add_printer(printer.to_web())
            if webid:
                printer.set_webid(webid)
            else:
                sleep(10)
            printer = Printer.get_by_id(id, fresh=True)
        job_thread = JobCollector(id, webapi)
        job_thread.start()
        log          = hub.log
        log.log("PrinterCollector starting for printer " + str(id))
        failures     = 0
        #url          = "http://" + ip + ":" + port
        prev_data    = {}
        while(True):
            printer = Printer.get_by_id(id, fresh=True)
            ip     = printer.ip
            port   = printer.port
            key    = printer.key
            jobs   = printer.jobs
            status = printer.status
            cjob   = printer.current_job()
            if self.stopped:
                webapi.patch_printer(printer.to_web())
                log.log("PrinterCollector stop signal received for "
                        + str(id) + ". Telling JobCollector to stop.")
                job_thread.stop()
                job_thread.join()
                log.log("JobCollector stopped."
                        +" Exiting PrinterCollector.")
                return 0
            # If status is set to completed, don't do anyting else
            if status in ["completed", "cancelled"]:
                if job_thread.is_alive():
                    job_thread.join(10)
                    if job_thread.is_alive():
                        log.log("ERROR: Printer is " + status 
                                + " but JobCollector is still running")
                    data = printer.to_web()
                    if cmp(prev_data,data):
                        prev_data = data.copy()
                        webapi.patch_printer(printer.to_web())
                    sleep(5)
            if not job_thread.is_alive() and cjob != None\
                    and status not in ["errored", "cancelled",
                                                    "completed"]:
                log.log("JobCollector thread died for "
                        + str(id) + ". Starting new JobCollector.")
                job_thread = JobCollector(id, webapi)
                job_thread.start()
            url    = ip + ":" + str(port)
            response = octopi.get_printer_info(url, key)
            if response != None:
                failures = 0
            else:
                failures += 1
                if failures > 5:
                    printer = Printer.get_by_id(id, fresh=True)
                    if printer.state("offline"):
                        data = printer.to_web()
                        if cmp(prev_data, data):
                            prev_data = data.copy()
                            webapi.patch_printer(data)
                        log.log("ERROR: Could not collect printer"
                              + " data from printer "+str(id))
                        job_thread.join()
                        log.log("JobCollector stopped."
                                +" Exiting PrinterCollector.")
                        return -1
                sleep(5)
                continue
            if response.status_code != 200:
                log.log("ERROR: Response from "
                        + str(id) + " returned status code "
                        + str(response.status_code) + " on "
                        + response.url)
            else:
                #data = response.json()
                state = response.json()
                printer = Printer.get_by_id(id, fresh=True)
                if printer.state_from_octopi(state):
                    data = printer.to_web()
                    if prev_data.get("status") == "printing"\
                            and data.get("status") == "ready":
                                printer.state("completed")
                                continue
                    # Check to see if data is the same as last collected
                    # if so, do not send it
                    if cmp(prev_data, data):
                        prev_data = data.copy()
                        webapi.patch_printer(data)
            sleep(1)

    def stop(self):
        self.stopped = True

class JobCollector(threading.Thread):

    """Job Collector will continue to grab """

    def __init__(self, printer_id, webapi):
        """TODO: to be defined1. """
        threading.Thread.__init__(self)
        self.printer_id = printer_id
        job = Printer.get_by_id(printer_id, fresh=True).current_job()
        self.stopped = False
        self.webapi = webapi
        if job:
            self.status = job.status
        else:
            self.status = None

    def run(self):
        id = self.printer_id
        webapi = self.webapi
        log          = hub.log
        log.log("JobCollector starting for printer " + str(id))
        failures     = 0
        #url          = "http://" + ip + ":" + port
        prev_data    = {}
        recent_json  = None
        while(True):
            if self.stopped:
                log.log("JobCollector stop signal received for "
                        + str(id) + ", exiting.")
                return 0
            printer = Printer.get_by_id(id, fresh=True)
            ip     = printer.ip
            port   = printer.port
            key    = printer.key
            jobs   = printer.jobs
            status = printer.status
            cjob   = printer.current_job()
            url    = ip + ":" + str(port)
            #If no current job, simply stop tracking. PrinterCollector
            # will spawn a new job thread when needed
            if cjob == None:
                log.log("No current job exists for " + str(id)
                        + ". JobCollector exiting.")
                return 0
            #If printer status is set to completed, cancelled,
            #or errored, exit. a new job thread will be spawned
            #by printer collector when needed
            if status == "offline":
                return 0
            if status == "completed"\
                and prev_data.get("data")\
                    .get("progress").get("completion") == 100:
                # this ensures it will have updated to the web api
                cjob.state("completed")
                data = cjob.to_web(recent_json)
                i = 0
                # Try to update to web api 10 times
                while not webapi.patch_job(data) and i < 10:
                    i+=1
                    sleep(5)
                return 0
            if status == "cancelled":
                cjob.state("errored")
                data = cjob.to_web(recent_json)
                i = 0
                # Try to update to web api 10 times
                while not webapi.patch_job(data) and i < 10:
                    i+=1
                    sleep(5)
                return 0
            if status == "errored":
                cjob.state("errored")
                data = cjob.to_web(recent_json)
                i = 0
                # Try to update to web api 10 times
                while not webapi.patch_job(data) and i < 10:
                    i+=1
                    sleep(5)
                return 0
            if status == "paused":
                cjob.state("paused")
            if status == "printing":
                cjob.state("printing")
            response = octopi.get_job_info(url, key)
            if response != None:
                failures = 0
            else:
                failures += 1
                log.log("ERROR: Could not collect"
                       + " job data from printer " + str(id)
                       + " on " + url )
                if failures > 5:
                    cjob.state("errored")
                    webapi.patch_job(cjob.to_web(recent_json))
                    return -1
            if response.status_code != 200:
                log.log("ERROR: Response from "
                        + str(id) + " returned status code "
                        + str(response.status_code) + " on "
                        + response.url)
            else:
                recent_json = response.json()
                data = cjob.to_web(recent_json)
                if data != None:
                    # Check to see if data is the same as last collected
                    # if so, do not send it
                    if cmp(prev_data, data):
                        prev_data = data.copy()
                        webapi.patch_job(data)
                        #print(data)
                else:
                    log.log("ERROR: Did not get proper job data from "
                            + str(id))
                    sleep(10)
            sleep(1)

    def stop(self):
        self.stopped = True

def get_temp(node_ip, gpio):
    """Creates request to dht node for data"""

    url = "http://"+str(node_ip)+"/gpio/"+str(gpio)+"/dht"
    response = requests.get(url, timeout=10)
    data = json.loads(response.text)
    temp = data['temp']
    humidity = data['humi']
    return temp, humidity #data


def get_gpio(node_ip, gpio, type):
    """Creates request to node for data"""

    url = "http://"+str(node_ip)+"/gpio/"+str(gpio)+"/"+type
    response = requests.get(url, timeout=10)
    data = json.loads(response.text)
    if data['data']:
        return data["data"]
    return "{'data':error}"


def node_data_collector(id, ip):
    """Should spawn as its own thread for each node
    that calls activate. Collects data from the node every
    second and dumps it into the send channel.

    """
    nodes        = hub.nodes.nodes
    log          = hub.log
    failures     = 0
    #print str(hub.print_enabled)
    #TODO a lot of this code is fulling working/tested but general idea is there
    while(True):
        # load the json from the chip
        if failures > 20:
            log.log("ERROR: Have failed communication 20 times in a row."
                  + " Closing connection with " + str(id))
            with nodes.lock:
                if nodes.data.has_key(id):
                    nodes.data.pop(id)
            return
        try:
            #TODO: get all sensors attached to node then call the correct
            #method to get data
            results = Sensor.query.filter_by(node_id=nid).all()
            json_results = []

            for result in results:
                if result.sensor_type == 'temp':
                    temp, humidity = get_temp(ip, result.pin)
                else:
                    data = get_gpio(ip, result.pin, result.sensor_type)
            failures = 0
        except requests.Timeout:
            failures += 1
            log.log("ERROR: Timeout occured when communicating with "
                    + str(id) + ".")
            continue
        except requests.ConnectionError:
            failures += 1
            with nodes.lock:
                if (ip == nodes.data[id]["ip"]):
                    log.log("ERROR: Lost Connection to "
                            + str(id) + ".")#" Thread exiting...")
            continue
    # Start handling of data here.
    """
        if response.status_code != requests.codes.ok:
            log.log("ERROR: Response from "
                    + str(id) + " returned status code "
                    + response.status_code)

        else:
            r_json = response.json()
            #TODO: Could break current implementation
            #send_channel.send({
            #    id: {
            #        pertype : r_json.get("data")
            #    }
            #})
    """
    time.sleep(1)

def get_extension(name):
    """Returns the extension of a file.
    :path: path of file to get the extension of
    :returns: file extension

    """
    ext = name.rsplit('.', 1)[1]
    return ext
    
