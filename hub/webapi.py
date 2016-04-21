#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import hub

def add_job(web_url, headers, job):
    '''Will add a job to the WebAPI.
    Handles errors and logs.
    web_url: Base webaddress of server, or ip
    :returns: Tuple of boolean of success and 
              status code of response. Status code
              is None if no response

    '''
    printer_id = job.get('printer')
    job_id = job.get('id')
    url = web_url + '/printers/' + str(printer_id) + '/jobs'
    try:
        r = requests.post(url, headers=headers,
                            json=job, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url
                + ' Unable to add job ' + str(job_id))
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + ' Unable to add job ' + str(job_id))
        return False, None
    if r.status_code != requests.codes.created:
        log.log('ERROR: Job ' + str(job_id) + ' not created.'
                + ' Server responded with ' + str(r.status_code)
                + ' on ' + url)
        return False, r.status_code
    log.log('Added job ' + str(job_id) + ' to ' + url)
    return True, r.status_code

def patch_job(web_url, headers, job):
    '''Will updated a job on the WebAPI.
    Handles errors and logs.
    web_url: Base webaddress of server, or ip
    :returns: Tuple of boolean of success and 
              status code of response. Status code
              is None if no response

    '''
    printer_id = job.get('printer')
    job_id = job.get('id')
    url = web_url + '/jobs/' + str(job_id)
    try:
        r = requests.patch(url, headers=headers,
                            json = job, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to update job' + str(job_id) + '.')
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + ' Unable to update job' + str(job_id) + '.')
        return False, None
    if r.status_code == requests.codes.unauthorized:
        log.log('ERROR: Job ' + str(job_id) + ' not updated.'
                + ' Unauthorized on ' + url)
        return False, r.status_code
    elif r.status_code != requests.codes.ok:
        log.log('ERROR: Job ' + str(job_id) + ' not updated.'
                + ' Server responded with ' + str(r.status_code)
                + ' on ' + url)
        return False, r.status_code
    log.log('Updated job ' + str(job_id) + ' on ' + url)
    return True, r.status_code

def add_printer(web_url, headers, printer):
    '''Add a printer on the web api
    web_url: Base webaddress of server, or ip
    :returns: Tuple of boolean of success and 
              status code of response. Status code
              is None if no response

    '''
    hub_id = hub.ID
    uuid = printer.get('uuid')
    url = web_url + '/hubs/' + str(hub_id) + '/printers'
    try:
        r = requests.post(url, headers=headers,
                            json=printer, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to add printer ' + str(uuid) + '.')
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to add printer ' + str(uuid) + '.')
        return False, None
    if r.status_code != requests.codes.created:
        log.log('ERROR: Printer ' + str(uuid) + ' not added.'
                + ' Server responded with ' + str(r.status_code) 
                + ' on ' + url)
        return False, r.status_code
    log.log('Added printer ' + str(uuid) + ' to ' + url )
    return True, r.status_code

def patch_printer(web_url, headers, printer):
    '''Patch a printer on the web api
    web_url: Base webaddress of server, or ip
    :returns: Tuple of boolean of success and 
              status code of response. Status code
              is None if no response

    '''
    uuid = printer.get('id')
    url = web_url + '/printers/' + str(uuid) 
    try:
        r = requests.post(url, headers=headers,
                            json=printer, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to update printer ' + str(uuid) + '.')
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to update printer ' + str(uuid) + '.')
        return False, None
    if r.status_code != requests.codes.created:
        log.log('ERROR: Printer ' + str(uuid) + ' not updated.'
                + ' Server responded with ' + r.status_code 
                + ' on ' + url)
        return False, r.status_code
    log.log('Updated printer ' + str(uuid) + ' on ' + url )
    return True, r.status_code
