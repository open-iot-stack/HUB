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
        self.stopped = False
        self.webapi = webapi

    def run(self):
        id = self.printer_id
        webapi = self.webapi
        printer = Printer.get_by_id(id)
        # loop until the printer has a webid, otherwise we can't update
        while priner.webid == None:
            webid = webapi.add_printer(printer.to_web(None))
            if webid:
                printer.set_webid(webid)
            printer = Printer.get_by_id(id)
        job_thread = JobCollector(id, webapi)
        job_thread.start()
        log          = hub.log
        log.log("PrinterCollector starting for printer " + str(id))
        failures     = 0
        #url          = "http://" + ip + ":" + port
        prev_data    = {}
        while(True):
            if self.stopped:
                log.log("PrinterCollector stop signal received for "
                        + str(id) + ". Telling JobCollector to stop.")
                job_thread.stop()
                job_thread.join()
                log.log("JobCollector stopped."
                        +" Exiting PrinterCollector.")
                return 0
            if not job_thread.is_alive():
                log.log("ERROR: JobCollector thread died for "
                        + str(id) + ". Starting new JobCollector.")
                job_thread = JobCollector(id, webapi)
                job_thread.start()

            printer = Printer.get_by_id(id)
            ip     = printer.ip
            port   = printer.port
            key    = printer.key
            jobs   = printer.jobs
            status = printer.status
            url    = ip + ":" + str(port)
            response = octopi.get_printer_info(url, key)
            if response:
                failures = 0
            else:
                printer.state("Error")
                failures += 1
                log.log("ERROR: Could not collect printer"
                      + " data from printer "+str(id)
                      + " on " + url )
                if failures > 20:
                    printer.state("Closed on Error")
                    log.log("ERROR: Have failed communication"
                            + " 20 times in a row for printer "
                            + str(id)
                            + ". Closing JobCollector if alive.")
                    job_thread.stop()
                    job_thread.join()
                    log.log("JobCollector stopped."
                            +" Exiting PrinterCollector.")
                    return -1
                sleep(1)
                continue
            if response.status_code != 200:
                log.log("ERROR: Response from "
                        + str(id) + " returned status code "
                        + response.status_code + " on "
                        + url)
            else:
                #data = response.json()
                state = response.json()
                printer.state(state['text'])
                data = printer.to_web(state)
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
        self.stopped = False
        self.webapi = webapi

    def run(self):
        id = self.printer_id
        webapi = self.webapi
        log          = hub.log
        log.log("JobCollector starting for printer " + str(id))
        failures     = 0
        #url          = "http://" + ip + ":" + port
        prev_data    = {}
        while(True):
            if self.stopped:
                log.log("JobCollector stop signal received for "
                        + str(id) + ", exiting.")
                return 0
            printer = Printer.get_by_id(id)
            ip     = printer.ip
            port   = printer.port
            key    = printer.key
            jobs   = printer.jobs
            status = printer.status
            url    = ip + ":" + str(port)

            response = octopi.get_job_info(url, key)
            if response:
                failures = 0
            else:
                failures += 1
                log.log("ERROR: Could not collect"
                       + " job data from printer " + str(id)
                       + " on " + url )
                if failures > 20:
                    log.log("ERROR: Have failed communication"
                            + " 20 times in a row."
                            + " Closing connection with " + str(id))
                    return -1
                sleep(1)
                continue
            if response.status_code != requests.codes.ok:
                log.log("ERROR: Response from "
                        + str(id) + " returned status code "
                        + response.status_code + " on "
                        + url)
            else:
                job = printer.current_job()
                data = job.to_web(response.json())
                if data != None:
                    # Check to see if data is the same as last collected
                    # if so, do not send it
                    if cmp(prev_data, data) and data.get('id') != 0:
                        prev_data = data.copy()
                        webapi.patch_job(data)
                else:
                    log.log("ERROR: Did not get proper job data from"
                            + str(id))
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

def start_new_job(id,job_id,fpath,loc=octopi.local):
    """Function that will take care of everything
    to print a file that exists on the hub.
    If current job is not the job_id, returns false
    :id: printer id to get data from
    :job_id: job id that use believes should be started
    :fpath: filepath to the new file to start
    :returns: None

    """
    printer = Printer.get_by_id(id)
    ip   = printer.ip
    port = printer.port
    key  = printer.key
    jobs = printer.jobs
    log  = hub.log
    url = ip + ":" + str(port)
    if job_id != printer.current_job().id:
        log.log("ERROR: Job " + str(id) +
                "requested to be started was not the next job")
        return False
    r = octopi.upload_file(url, key, fpath, loc)
    if r == None:
        log.log("ERROR: Did not have a response from " + str(id)
                + ". File upload canceled for " + fpath + ".")
        return False
    if r.status_code != 201:
        log.log("ERROR: Could not upload file " + fpath
                + ". Return code from printer " + str(r.status_code))
        return False
    data = r.json()
    fname = data['files'][loc]['name']
    ext = get_extension(fname)
    if ext in ['stl']:
        r = octopi.slice_and_print(url, key, fname, loc)
    elif ext in ['gco']:
        r = octopi.select_and_print(url, key, fname, loc)
    if r == None:
        log.log("ERROR: Did not have a response from " + str(id)
                + ". Job start canceled for job " + str(job_id) + ".")
        return False
    if r.status_code != 204:
        log.log("ERROR: Job start failed for " + str(job_id)
                + ". Return code from printer " + str(r.status_code)
                + ". Is the printer already printing?")
        return False
    return True

def get_extension(path):
    """Returns the extension of a file.
    :path: path of file to get the extension of
    :returns: file extension

    """
    ext = name.rsplit('.', 1)[1]
    return ext
    
