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
from tasks import Command
from hub import app

class PrinterCollector(threading.Thread):

    """Printer Collector will continue to grab """

    def __init__(self, printer_id, webapi, log):
        """TODO: to be defined1. """
        threading.Thread.__init__(self)
        self.printer_id = printer_id
        printer = Printer.get_by_id(printer_id)
        status = printer.status
        self.stopped = False
        self.webapi = webapi
        self.log    = log
        self.lock = threading.Lock()

    def run(self):
        id = self.printer_id
        webapi = self.webapi
        log          = self.log
        printer = Printer.get_by_id(id, fresh=True)
        # loop until the printer has a webid,
        # otherwise we can't update
        while printer.webid == None:
            webid = webapi.add_printer(printer.first_web())
            if webid:
                printer.set_webid(webid)
            else:
                sleep(10)
            printer = Printer.get_by_id(id, fresh=True)
        job_thread = JobCollector(id, webapi, log)
        job_thread.start()
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
                        job_thread.stop()
                data = printer.to_web()
                if cmp(prev_data,data):
                    prev_data = data.copy()
                    webapi.patch_printer(printer.to_web())
            if not job_thread.is_alive() and cjob != None\
                    and status not in ["errored", "cancelled",
                                                    "completed"]:
                log.log("JobCollector thread died for "
                        + str(id) + ". Starting new JobCollector.")
                job_thread = JobCollector(id, webapi, log)
                job_thread.start()
            url    = ip + ":" + str(port)
            response = octopi.get_printer_info(url, key)
            if response != None:
                failures = 0
            else:
                failures += 1
                if failures > 2:
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

    def __init__(self, printer_id, webapi, log):
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
        self.log = log

    def run(self):
        id = self.printer_id
        webapi = self.webapi
        log          = self.log
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
            if cjob.status == "completed":
                return 0
            if cjob.status == "cancelled":
                return 0
            if cjob.status == "queued":
                t = Command(id, log, "start", webapi)
                t.start()
            if cjob.status == "errored" and status == "ready":
                printer.remove_job(cjob.id)
            #If printer status is set to completed, cancelled,
            #or errored, exit. a new job thread will be spawned
            #by printer collector when needed
            if status == "offline":
                cjob.state("errored")
                data = cjob.to_web(recent_json)
                if data == None:
                    data = cjob.to_web(None)
                i = 0
                # Try to update to web api 10 times
                while not webapi.patch_job(data) and i < 10:
                    i+=1
                    sleep(5)
                return 0
            if status == "completed" and prev_data\
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
                cjob.state("cancelled")
                data = cjob.to_web(recent_json)
                if data == None:
                    data = cjob.to_web(None)
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
                continue
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

class NodeCollector(threading.Thread):

    """NodeCollector will collect sensor information
    from the sensors associated with it"""

    def __init__(self, node_id, webapi, log):
        """TODO: to be defined1.

        """
        threading.Thread.__init__(self)
        self.node_id = node_id
        self.webapi = webapi
        self.stopped = False
        self.log = log

    def stop(self):
        self.stopped = True

    def run(self):
        """TODO: Docstring for run.
        :returns: TODO

        """
        id     = self.node_id
        webapi = self.webapi
        log    = self.log
        node   = Node.get_by_id(id)
        log.log("NodeCollector starting for node " + str(id))
        sleep(10)
        failures = 0
        while(True):
            node    = Node.get_by_id(id, fresh=True)
            ip      = node.ip
            sensors = node.sensors
            if self.stopped == True:
                log.log("NodeCollector for node " + str(id)
                        + " was requested to stop. Exiting...")
                return 0
            for sensor in sensors:
                pin         = sensor.pin
                webid       = sensor.webid
                sensor_type = sensor.sensor_type
                if pin == None or sensor_type == None:
                    continue
                if sensor_type in ["TEMP", "DOOR", "HUMI", "TRIG"]:
                    url = sensor.get_url()
                elif sensor_type in ["LED"]:
                    printer = Printer.get_by_id(node.printer_id)
                    if printer:
                        if printer.status in ["completed", "cancelled"]:
                            url = sensor.led_flash()
                        else:
                            url = sensor.led_on()
                    else:
                        continue
                elif sensor_type in ["POWER"]:
                    url = sensor.power_on()
                else:
                    continue
                try:
                    response = requests.get(url, timeout=10)
                except requests.ConnectionError:
                    log.log("ERROR: Could not connect to " + url)
                    response = None
                except requests.exceptions.Timeout:
                    log.log("ERROR: Timeout occured on " + url)
                    response = None
                if response == None:
                    failures += 1
                    if failures > 10:
                        log.log("ERROR: Could not collect"
                                + " sensor data from node " + str(id)
                                + ". NodeCollector exiting...")
                        return -1
                    continue
                if response.status_code != 200:
                    log.log("ERROR Response from " 
                            + str(id) + " returned status code "
                            + str(response.status_code) + " on "
                            + response.url)
                else:
                    recent_json = response.json()
                    data = sensor.to_web(recent_json)
                    if data != None:
                        webapi.add_data(data)
                sleep(3)
            sleep(3)


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
