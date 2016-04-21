#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import hub

def add_job(web_url, headers, job):
    '''Will add a job to the WebAPI.
    Handles errors and logs.
    web_url: Base webaddress of server, or ip
    :returns:None if Job failed and cannot be added,
             False if Job was not created but is back in queue,
             True if Job was added on server successfully.

    '''
    url = web_url + '/printers' + str(job.get('printer'))
    r = None
    try:
        r = requests.post(url, headers=headers,
                            json=job, timeout=3)
    except requests.ConnectionError:
        log.log("ERROR: Could not connect to " + url 
                + ". Readding to queue.")
        try:
            hub.send_channel.send_exn({'add_job', job})
            return False
        except channel.SendException:
            log.log("MAXIMUM ERROR: Channel is full."
                    + " Unable to add job " + str(job_id))
            return None
    except requests.exceptions.Timeout:
        log.log("ERROR: Connection timeout when contacting "
                + url + ". Readding to queue.")
        try:
            hub.send_channel.send_exn({'add_job', job})
        return False
        except channel.SendException:
            log.log("MAXIMUM ERROR: Channel is full."
                    + " Unable to add job " + str(job_id))
            return None
    if r:
        if r.status_code == requests.codes.unauthorized:
            log.log("ERROR: Unauthorized on " + url
                    + ". Readding to queue. Getting new headers.")
            headers = access.get_headers(api_key, headers)
            try:
                hub.send_channel.send_exn({'add_job', job})
                return False
            except channel.SendException:
                log.log("MAXIMUM ERROR: Channel is full."
                        + " Unable to add job " + str(job_id))
                return None
        elif r.status_code != requests.codes.created:
            log.log("ERROR: Job " + str(job_id) + " not created."
                    + ". Readding to queue.")
            headers = access.get_headers(api_key, headers)
            try:
                hub.send_channel.send_exn({'add_job', job})
                return False
            except channel.SendException:
                log.log("MAXIMUM ERROR: Channel is full."
                        + " Unable to add job " + str(job_id))
                return None
    log.log("Added job " + str(job_d) + " to " + url)
    return True

def patch_job(web_url, headers, job)
    '''Will updated a job on the WebAPI.
    Handles errors and logs.
    web_url: Base webaddress of server, or ip
    :returns:None if Job failed and cannot be updated
             False if Job was not updated but is back in queue,
             True if Job was update on server successfully.

    '''
    printer_id = job.get('printer')
    job_id = job.get("id")
    url = web_url + "/jobs/" + job_id
    r = None
    try:
        r = requests.patch(url, headers=headers,
                            json = job, timeout=3)
    except requests.ConnectionError:
        log.log("ERROR: Could not connect to " + url 
                + ". Unable to update job.")
        return None
    except requests.exceptions.Timeout:
        log.log("ERROR: Connection timeout when contacting "
                + url + ". Unable to update job.")
        return None
    if r:
        if r.status_code == requests.codes.unauthorized:
            log.log("ERROR: Unauthorized on " + url
                    + ". Readding to queue. Getting new headers.")
            try:
                hub.send_channel.send_exn({'add_job', job})
                return False
            except channel.SendException:
                log.log("MAXIMUM ERROR: Channel is full."
                        + " Unable to add job " + str(job_id))
                return None
        elif r.status_code != requests.codes.ok:
            log.log("ERROR: Job " + str(job_id) + " not updated.")
            return False
    log.log("Updated job " + str(job_id) + " on " + url)
    return True

def add_printer(web_url, headers, printer):
    '''Add a printer on the web api
    web_url: Base webaddress of server, or ip
    :returns:None if Printer failed and cannot be added,
             False if Printer was not created but is back in queue,
             True if Printer was added on server successfully.

    '''
    try:
        r = requests.post(url, headers=headers,
                            json=printer, timeout=3)
    except requests.ConnectionError:
        log.log("ERROR: Could not connect to " + url 
                + ". Unable to add printer " + str(uuid)".")
    except requests.exceptions.Timeout:
        log.log("ERROR: Connection timeout when contacting "
                + url + ". Unable to add printer " + str(uuid)".")
    log.log("Added printer " + str(uuid) + " to " + url )

def patch_printer(web_url, headers, printer):
    '''Patch a printer on the web api
    web_url: Base webaddress of server, or ip
    :returns:None if Printer failed and cannot be updated,
             False if Printer was not updated but is back in queue,
             True if Printer was updated on server successfully.

    '''
    url = web_url + "/printers/" + str(hub.uuid) 
    uuid = printer.get('id')
    try:
        r = requests.post(url, headers=headers,
                            json=printer, timeout=3)
    except requests.ConnectionError:
        log.log("ERROR: Could not connect to " + url 
                + ". Unable to update printer " + str(uuid)".")
    except requests.exceptions.Timeout:
        log.log("ERROR: Connection timeout when contacting "
                + url + ". Unable to update printer " + str(uuid)".")
    log.log("Updated printer " + str(uuid) + " to " + url )
