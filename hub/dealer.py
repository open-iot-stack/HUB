#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import hub
import thread
import threading
import channel
import requests
import webapi
import octopifunctions as octopi
from message_generator import MessageGenerator
from parse import parse_job_status, parse_printer_status
from time import sleep
from flask import json
from sqlalchemy.orm import sessionmaker
from models import Printer, Node, Job
import auth
from hub import app

class PrinterCollector(threading.Thread):

    """Printer Collector will continue to grab """

    def __init__(self, printer_id):
        """TODO: to be defined1. """
        threading.Thread.__init__(self)
        self.printer_id = printer_id
        self.stopped = False

    def run(self):
        id = self.printer_id
        job_thread = JobCollector(id)
        job_thread.start()
        send_channel = hub.send_channel
        log          = hub.log
        log.log("printer_data_collector starting for printer " + str(id))
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
                thread.exit()
            if not job_thread.is_alive():
                log.log("ERROR: JobCollector thread died for "
                        + str(id) + ". Starting new JobCollector.")
                job_thread = JobCollector(id)
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
                    thread.exit()
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
                    send_channel.send({ "printer": data })
            sleep(1)

    def stop(self):
        self.stopped = True

class JobCollector(threading.Thread):

    """Job Collector will continue to grab """

    def __init__(self, printer_id):
        """TODO: to be defined1. """
        threading.Thread.__init__(self)
        self.printer_id = printer_id
        self.stopped = False

    def run(self):
        id = self.printer_id
        send_channel = hub.send_channel
        log          = hub.log
        log.log("job_data_collector starting for printer " + str(id))
        failures     = 0
        #url          = "http://" + ip + ":" + port
        prev_data    = {}
        while(True):
            if self.stopped:
                log.log("JobCollector stop signal received for "
                        + str(id) + ", exiting.")
                thread.exit()
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
                    thread.exit()
                sleep(1)
                continue
            if response.status_code != requests.codes.ok:
                log.log("ERROR: Response from "
                        + str(id) + " returned status code "
                        + response.status_code + " on "
                        + url)
            else:
                data = parse_job_status(response.json())
                # Check to see if data is the same as last collected
                # if so, do not send it
                if cmp(prev_data, data):
                    prev_data = data
                    prev_data = data.copy()
                    send_channel.send({"patch_job": data})
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
    send_channel = hub.send_channel
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
            thread.exit()
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

def data_receiver():
    """Should spawn as its own thread. Will take data that
    is collected by the nodes and send it to the Web API.
    Also is in charge of logging data based on UUID.

    """
    log = hub.log
    domain  = "www.stratusprint.com"
    web_url = "http://" + domain
    api_key = hub.API_KEY
    base_url = hub.webapi
    #TODO set base_url from hub and commandline argument
    for message in MessageGenerator(hub.recv_channel):
        headers = auth.get_headers(api_key, base_url=auth.dev_url)
        if message.has_key("add_job"):
            job = message.get('add_job')
            if job:
                ret,code = webapi.add_job(web_url, headers, job)
                if ret == False:
                    if code == requests.codes.unauthorized:
                        headers = get_headers(api_key, base_url=base_url)
                    #TODO readd to queue
            else:
                log.log("ERROR: Job to add was empty")

        if message.has_key("patch_job"):
            job = message.get("patch_job")
            if job:
                ret,code = webapi.patch_job(web_url, headers, job)
                if ret == False:
                    if code == requests.codes.unauthorized:
                        headers = get_headers(api_key, base_url=base_url)
            else:
                log.log("ERROR: Job to update was empty")

        if message.has_key("add_printer"):
            printer = message.get("add_printer")
            if printer:
                ret,code = webapi.add_printer(web_url, headers,
                                                    printer)
                if ret == False:
                    if code == requests.codes.unauthorized:
                        headers = get_headers(api_key, base_url=base_url)
            else:
                log.log("ERROR: Printer to add was empty")

        if message.has_key('patch_printer'):
            printer = message.get('patch_printer')
            if printer:
                ret,code = webapi.patch_printer(web_url, headers,
                                                    printer)
                if ret == False:
                    if code == requests.codes.unauthorized:
                        headers = get_headers(api_key, base_url=base_url)
            else:
                log.log("ERROR: Printer to printer was empty")

def upload_and_print(id,job_id,fpath,loc=octopi.local):
    """Function that will take care of everything
    to print a file that exists on the hub.
    If current job is not the job_id, returns false
    :printer: printer object to get data from
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
    url = "http://" + ip + ":" + str(port)
    if job_id != printer.current_job().id:
        log.log("ERROR: Job " + str(id) +
                "requested to be started was not the next job")
        return False
    r = octopi.upload_file(url, key, fpath, loc)
    if r == None:
        log.log("ERROR: Did not have a response from " + str(id)
                + ". File upload canceled for " + fpath + ".")
        return False
    if r.status_code != requests.codes.created:
        log.log("ERROR: Could not upload file " + fpath
                + ". Return code from printer " + str(r.status_code))
        return False
    data = r.json()
    fname = data['files'][loc]['name']
    #TODO fix this to work with gcode files as well
    r = slice_and_print(url, key, fname, loc)
    if r == None:
        log.log("ERROR: Did not have a response from " + str(id)
                + ". File slice canceled for " + fname + ".")
        return False
    if r.status_code != requests.codes.accepted:
        log.log("ERROR: Slice and print did not work for " + str(id)
                + ". Return code from printer " + str(r.status_code)
                + ". Is the printer already printing?")
        return False
    return True
