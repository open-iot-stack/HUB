#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import hub
import thread
import channel
import requests
import webapi
import octopifunctions as octopi
from message_generator import MessageGenerator
from parse import parse_job_status, parse_printer_status
from time import sleep
import auth
from hub import app

def printer_data_collector(printer):
    uuid   = printer.get("uuid")
    ip     = printer.get("ip")
    port   = printer.get("port")
    key    = printer.get("key")
    jobs   = printer.get("jobs")
    cjob   = printer.get("cjob")
    status = printer.get("status")
    printers     = hub.printers.printers
    send_channel = hub.send_channel
    log          = hub.log
    log.log("printer_data_collector starting for printer " + str(uuid))
    failures     = 0
    #url          = "http://" + ip + ":" + port
    url          = ip + ":" + str(port)
    prev_data    = {}
    while(True):
        if failures > 20:
            log.log("ERROR: Have failed communication 20 times in a row."
                  + " Closing connection with " + str(uuid))
            with printers.lock:
                if printers.data.has_key(uuid):
                    # SET STATUS TO OFFLINE
                    status["data"]["state"]["text"] = "Offline"
                    pass
            thread.exit()
        response = octopi.get_printer_info(url, key)
        if response:
            failures = 0
        else:
            sleep(1)
            failures += 1
            log.log("ERROR: Could not collect printer"
                  + " data from printer "+str(uuid))
            continue
        if response.status_code != requests.codes.ok:
            log.log("ERROR: Response from "
                    + str(uuid) + " returned status code "
                    + response.status_code + " on "
                    + url)
        else:
            #data = response.json()
            data = parse_printer_status(printer, response.json())
            # Check to see if data is the same as last collected
            # if so, do not send it
            if cmp(prev_data, data):
                printer["cjob"] = data
                prev_data = data.copy()
                send_channel.send({ "printer": data })
        sleep(1)


def job_data_collector(printer):
    uuid = printer.get("uuid")
    ip   = printer.get("ip")
    port = printer.get("port")
    key  = printer.get("key")
    jobs = printer.get("jobs")
    cjob = printer.get("cjob")
    status = printer.get("status")
    printers     = hub.printers.printers
    send_channel = hub.send_channel
    log          = hub.log
    log.log("job_data_collector starting for printer " + str(uuid))
    failures     = 0
    #url          = "http://" + ip + ":" + port
    url          = ip + ":" + str(port)
    prev_data    = {}
    while(True):
        if failures > 20:
            log.log("ERROR: Have failed communication 20 times in a row."
                  + " Closing connection with " + str(uuid))
            with printers.lock:
                if printers.data.has_key(uuid):
                    status["data"]["state"]["text"] = "Offline"
            thread.exit()
        response = octopi.get_job_info(url, key)
        if response:
            failures = 0
        else:
            sleep(1)
            failures += 1
            log.log("ERROR: Could not collect"
                   + " job data from printer " + str(uuid))
            continue
        if response.status_code != requests.codes.ok:
            log.log("ERROR: Response from "
                    + str(uuid) + " returned status code "
                    + response.status_code + " on "
                    + url)
        else:
            data = parse_job_status(response.json(), printer["cjob"].copy())
            # Check to see if data is the same as last collected
            # if so, do not send it
            if cmp(printer["cjob"], data):
                printer["cjob"] = data
                prev_data = data.copy()
                send_channel.send({"patch_job": data})
        sleep(1)

def get_temp(node_ip, gpio):
    """Creates request to dht sensor for data"""

    url = "http://"+str(node_ip)+"/"+str(gpio)+"/dht"
    response = requests.get(url, timeout=10)
    data = json.loads(response.text)
    temp = data['data']['temp']
    humidity = data['data']['humi']
    return temp, humidity #data

    #req = Request(node_ip+"/"+gpio+"/dht")
    #response_body = urlopen(req).read()
    #data = json.loads(response_body)
    #temp = data['data']['temp']
    #humidity = data['data']['humi']
    #print("temp: "+temp+" humidity: "+ humi)
    #return data

def sensor_data_collector(uuid, ip, pertype):
    """Should spawn as its own thread for each sensor
    that calls activate. Collects data from the sensor every
    second and dumps it into the send channel.

    """
    nodes        = hub.nodes.nodes
    send_channel = hub.send_channel
    log          = hub.log
    failures     = 0
    #print str(hub.print_enabled)
    #TODO fix url to be the correct call based on type
    #url = "http://" + ip + "/GPIO/2"
    #TODO a lot of this code is fulling working/tested but general idea is there
    while(True):
        # load the json from the chip
        if failures > 20:
            log.log("ERROR: Have failed communication 20 times in a row."
                  + " Closing connection with " + str(uuid))
            with nodes.lock:
                if nodes.data.has_key(uuid):
                    nodes.data.pop(uuid)
            thread.exit()
        try:
            #need to find how we're getting the node_ip and fill in.
            temp, humidity = get_temp(ip, 1)
            failures = 0
        #TODO Talk to Nolan about how to handle these exceptions.
        #Can either be node or server side
        except requests.Timeout:
            failures += 1
            log.log("ERROR: Timeout occured when communicating with "
                    + str(uuid) + ".")
            continue
        except requests.ConnectionError:
            failures += 1
            with nodes.lock:
                if (ip == nodes.data[uuid]["ip"]):
                    log.log("ERROR: Lost Connection to "
                            + str(uuid) + ".")#" Thread exiting...")
            continue
    # Start handling of data here.

        if response.status_code != requests.codes.ok:
            log.log("ERROR: Response from "
                    + str(uuid) + " returned status code "
                    + response.status_code)

        else:
            r_json = response.json()
            send_channel.send({
                uuid: {
                    pertype : r_json.get("data")
                } 
            })
        time.sleep(1)

def data_receiver():
    """Should spawn as its own thread. Will take data that
    is collected by the sensors and send it to the Web API.
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

def upload_and_print(printer,job_id,fpath,loc=octopi.local):
    """Function that will take care of everything
    to print a file that exists on the hub.
    If current job is not the job_id, returns false
    :printer: printer object to get data from
    :job_id: job id that use believes should be started
    :fpath: filepath to the new file to start
    :returns: None

    """
    uuid = printer.get("uuid")
    ip   = printer.get("ip")
    port = printer.get("port")
    key  = printer.get("key")
    jobs = printer.get("jobs")
    cjob = printer.get("cjob")
    log  = hub.log
    url = "http://" + ip + ":" + str(port)
    if job_id != jobs.current().get("id"):
        return False
    r = octopi.upload_file(url, key, fpath, loc)
    if r == None:
        log.log("ERROR: Did not have a response from " + str(uuid)
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
        log.log("ERROR: Did not have a response from " + str(uuid)
                + ". File slice canceled for " + fname + ".")
        return False
    if r.status_code != requests.codes.accepted:
        log.log("ERROR: Slice and print did not work for " + str(uuid)
                + ". Return code from printer " + str(r.status_code)
                + ". Is the printer already printing?")
        return False
    printer["cjob"] = jobs.current()
    return True
