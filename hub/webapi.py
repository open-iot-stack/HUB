#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import hub
import auth
import printers
import nodes

#DO NOT EDIT HEADERS MANUALY
headers = {}

def update_headers(web_url):
    '''Updates the global headers object
    :web_url: Base webaddress of server, or ip
    :returns: boolean of success of update

    '''
    global headers
    api_key = hub.API_KEY
    headers = auth.get_headers(api_key, headers=headers,
                                    base_url=web_url)
    if headers:
        return True
    return False

def add_printer(web_url, printer):
    '''Add a printer on the web api
    :web_url: Base webaddress of server, or ip
    :printer: printer to be added to web api
    :returns: boolean of success

    '''
    hub_id = hub.ID
    printer_id = printer.get('id')
    url = web_url + '/hubs/' + str(hub_id) + '/printers'
    try:
        r = requests.post(url, headers=headers,
                            json=printer, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to add printer ' 
                + str(printer_id) + '.')
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to add printer '
                + str(printer_id) + '.')
        return False
    code = r.status_code
    # Handle error codes from web api
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Printer ' + str(printer_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        ret = update_headers(web_url)
        return add_printer(web_url, printer)
    if code == 404:
        # Hub is not registered. Updating headers should fix this.
        log.log('ERROR: Printer ' + str(printer_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        ret = update_headers(web_url)
        return add_printer(web_url, printer)
    if r.status_code != 201:
        # Catch all for if bad status codes
        log.log('ERROR: Printer ' + str(printer_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return False
    log.log('Added printer ' + str(printer_id) + ' to ' + url )
    return True

def patch_printer(web_url, printer):
    '''Patch a printer on the web api
    :web_url: Base webaddress of server, or ip
    :headers: headers for request to use
    :printer: printer to be updated on the web api
    :returns: boolean of success

    '''
    printer_id = printer.get('id')
    url = web_url + '/printers/' + str(printer_id) 
    try:
        r = requests.post(url, headers=headers,
                            json=printer, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to update printer '
                + str(printer_id) + '.')
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to update printer ' 
                + str(printer_id) + '.')
        return False
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Printer ' + str(printer_id) + ' not updated.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        ret = update_headers(web_url)
        return patch_printer(web_url, printer)
    if code == 404:
        # Printer is not registered. Adding printer instead
        log.log('ERROR: Printer ' + str(printer_id) + ' not updated.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return add_printer(web_url, printer)
    if code != 200:
        log.log('ERROR: Printer ' + str(printer_id) + ' not updated.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return False
    log.log('Updated printer ' + str(printer_id) + ' on ' + url )
    return True

def delete_printer(web_url, printer_id):
    '''Deletes a printer on the web api
    :web_url: TODO
    :printer_id: TODO
    :returns: TODO

    '''
    url = web_url + '/printers/' + str(printer_id) 
    try:
        r = requests.delete(url, headers=headers,
                            timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to update printer '
                + str(printer_id) + '.')
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to update printer '
                + str(printer_id) + '.')
        return False
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Printer ' + str(printer_id) + ' not deleted.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        ret = update_headers(web_url)
        return delete_printer(web_url, printer)
    if code == 404:
        # Printer is not registered. Adding printer also updates
        log.log('ERROR: Printer ' + str(printer_id) + ' not deleted.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        log.log('Printer wasn\'t found on server to delete'
                + ', faking it deleted')
        return True
    if code != 204:
        log.log('ERROR: Printer ' + str(printer_id) + ' not deleted.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return False
    log.log('Deleted printer ' + str(printer_id) + ' on ' + url )
    return True
    

def add_job(web_url, job):
    '''Will add a job to the WebAPI.
    Handles errors and logs.
    :web_url: Base webaddress of server, or ip
    :job:     job to be added to web api
    :returns: boolean of success

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
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + ' Unable to add job ' + str(job_id))
        return False
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Job ' + str(job_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        ret = update_headers(web_url)
        return add_job(web_url, job)
    if code == 404:
        # Printer not found. Get printer and add printer, then add job
        log.log('ERROR: Job ' + str(job_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        with printers.printers.lock:
            if printer_id in printers.printers.data:
                printer = printers.printers.data.get('printer')
            else:
                log.log('ERROR: Printer ' + str(printer_id)
                        + ' not found locally but ' + str(job_id)
                        + ' is registered as its job')
                return False
        ret = add_printer(web_url, printer)
        if ret:
            return add_job(web_url, job)
        else:
            return False
    if r.status_code != requests.codes.created:
        log.log('ERROR: Job ' + str(job_id) + ' not created.'
                + ' Server responded with ' + str(r.status_code)
                + ' on ' + url)
        return False
    log.log('Added job ' + str(job_id) + ' to ' + url)
    return True

def patch_job(web_url, headers, job):
    '''Will updated a job on the WebAPI.
    Handles errors and logs.
    :web_url: Base webaddress of server, or ip
    :headers: headers for request to use
    :job:     job to be updated on the web api
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

def delete_job(web_url, headers, job):
    '''Will delete a job on the WebAPI

    :web_url: Base webaddress of server, or ip
    :headers: headers for request to use
    :job:     job to be deleted to web api
    :returns: Tuple of boolean of success and 
              status code of response. Status code
              is None if no response

    '''
    printer_id = job.get('printer')
    job_id = job.get('id')
    url = web_url + '/jobs/' + str(job_id)
    try:
        r = requests.delete(url, headers=headers,
                            timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to delete job' + str(job_id) + '.')
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + ' Unable to delete job' + str(job_id) + '.')
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

def add_node(web_url, headers, node):
    '''Add a node to the web api
    :web_url: Base webaddress of server, or ip
    :headers: headers for request to use
    :node: node to be added to web api
    :returns: Tuple of boolean of success and 
              status code of response. Status code
              is None if no response

    '''
    hub_id = hub.ID
    node_id = node.get('id')
    url = web_url + '/hubs/' + str(hub_id) + '/sensors'
    try:
        r = requests.post(url, headers=headers,
                            json=node, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to add node ' + str(node_id) + '.')
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to add node ' + str(node_id) + '.')
        return False, None
    if r.status_code != requests.codes.created:
        log.log('ERROR: Node ' + str(node_id) + ' not added.'
                + ' Server responded with ' + str(r.status_code) 
                + ' on ' + url)
        return False, r.status_code
    log.log('Added Node ' + str(node_id) + ' to ' + url )
    return True, r.status_code

def patch_node(web_url, headers, node):
    '''Patch a node on the web api
    :web_url: Base webaddress of server, or ip
    :headers: headers for request to use
    :node: node to be updated on web api
    :returns: Tuple of boolean of success and 
              status code of response. Status code
              is None if no response

    '''
    node_id = node.get('id')
    url = web_url + '/sensors/' + str(node_id)
    try:
        r = requests.post(url, headers=headers,
                            json=node, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to update node ' + str(node_id) + '.')
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to update node ' + str(node_id) + '.')
        return False, None
    if r.status_code != requests.codes.created:
        log.log('ERROR: Node ' + str(node_id) + ' not updated.'
                + ' Server responded with ' + str(r.status_code) 
                + ' on ' + url)
        return False, r.status_code
    log.log('Updated Node ' + str(node_id) + ' to ' + url )
    return True, r.status_code
