#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hub
import thread
import requests
import octopifunctions as octopi
from message_generator import MessageGenerator

def printer_data_collector(uuid, ip, port, key):
    url = ip + ":" + port
    while(True):
        response = octopi.GetJobInfo(url, key)
        #TODO Add data into send channel. Talk to Aaron about change
        # changing responses from jobs to just be the pure response
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
    nlock        = hub.nodes.nlock
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
            log.log("ERROR: Have failed communication 20 times in a row. "
                   +"Closing connection with " + uuid)
            thread.exit()
        try:
            #need to find how we're getting the node_ip and fill in.
            temp, humidity = get_temp(ip, 1)
            failures = 0
        #TODO Talk to Nolan about how to handle these exceptions. Can either
        # be node or server side
        except requests.Timeout:
            failures += 1
            log.log("ERROR: Timeout occured when communicating with "
                    + uuid + ".")
            continue
        except requests.ConnectionError:
            failures += 1
            with nlock:
                if (ip == nodes[uuid]["ip"]):
                    log.log("ERROR: Lost Connection to "
                            + uuid + ".")#" Thread exiting...")
                    if nodes.has_key(uuid):
                        nodes.pop(uuid)
            continue
    # Start handling of data here.

        if response.status_code != requests.codes.ok:
            log.log("ERROR: Response from "
                    + uuid + " returned status code "
                    + response.status_code)

        else:
            if response.headers.get('content-type') != 'application/json':
                log.log("ERROR: Response from "
                        + uuid + " was not in json format")

            r_json = response.json()
            if (uuid != r_json.get("uuid")):
                # TODO: Make a get request on the chip
                # telling it to reconnect
                thread.exit()
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

    for message in MessageGenerator(hub.recv_channel):
        print message

