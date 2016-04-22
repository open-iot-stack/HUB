#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import hub
import auth

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
    if code != 201:
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
        return delete_printer(web_url, printer_id)
    if code == 404:
        # Printer is not registered. Claim deleted internally
        log.log('ERROR: Printer ' + str(printer_id) + ' not deleted.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        log.log('Printer wasn\'t found on server to delete'
                + ', faking it deleted')
        return True
    if code != 204:
        # Catch all if did not succeed and not handling
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
    if code != 201:
        # Catch all if did not succeed and not handling
        log.log('ERROR: Job ' + str(job_id) + ' not created.'
                + ' Server responded with ' + str(r.status_code)
                + ' on ' + url)
        return False
    log.log('Added job ' + str(job_id) + ' to ' + url)
    return True

def patch_job(web_url, job):
    '''Will updated a job on the WebAPI.
    Handles errors and logs.
    :web_url: Base webaddress of server, or ip
    :job:     job to be updated on the web api
    :returns: boolean of success

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
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + ' Unable to update job' + str(job_id) + '.')
        return False
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Job ' + str(job_id) + ' not updated.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        ret = update_headers(web_url)
        if ret:
            return patch_job(web_url, job)
        else:
            return False
    if code == 404:
        # Job not found. Just let the job finish 
        log.log('ERROR: Job ' + str(job_id) + ' not updated.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        log.log("ERROR: Job " + str(job_id) + " was not found "
                + "on " + str(url) + ". Something is really wrong.")
        return True
        #return add_job(web_url, job)
    elif code != 200:
        log.log('ERROR: Job ' + str(job_id) + ' not updated.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        return False
    log.log('Updated job ' + str(job_id) + ' on ' + url)
    return True

def delete_job(web_url, job):
    '''Will delete a job on the WebAPI
    :web_url: Base webaddress of server, or ip
    :job:     job to be deleted to web api
    :returns: boolean of success

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
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + ' Unable to delete job' + str(job_id) + '.')
        return False
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Job ' + str(job_id) + ' not deleted.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        ret = update_headers(web_url)
        if ret:
            return delete_job(web_url, job)
        else:
            return False
    if code == 404:
        # Job not found. Claim deleted internally
        log.log('ERROR: Job ' + str(job_id) + ' not deleted.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        log.log('Job wasn\'t found on server to delete'
                + ', faking it deleted')
        return True
    if code != 204:
        # Catch all if did not succeed and not handling
        log.log('ERROR: Job ' + str(job_id) + ' not updated.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        return False
    log.log('Updated job ' + str(job_id) + ' on ' + url)
    return True

def add_node(web_url, node):
    '''Add a node to the web api
    :web_url: Base webaddress of server, or ip
    :node: node to be added to web api
    :returns: boolean of success

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
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to add node ' + str(node_id) + '.')
        return False
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Node ' + str(node_id) + ' not added.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        ret = update_headers(web_url)
        if ret:
            return add_node(web_url, node)
        else:
            return False
    if code != 201:
        log.log('ERROR: Node ' + str(node_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return False
    log.log('Added Node ' + str(node_id) + ' to ' + url )
    return True

def patch_node(web_url, node):
    '''Patch a node on the web api
    :web_url: Base webaddress of server, or ip
    :node: node to be updated on web api
    :returns: boolean of success

    '''
    node_id = node.get('id')
    url = web_url + '/sensors/' + str(node_id)
    try:
        r = requests.patch(url, headers=headers,
                            json=node, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to update node ' + str(node_id) + '.')
        return False, None
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to update node ' + str(node_id) + '.')
        return False, None
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Node ' + str(node_id) + ' not updated.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        ret = update_headers(web_url)
        if ret:
            return patch_node(web_url, node)
        else:
            return False
    if code != 200:
        log.log('ERROR: Node ' + str(node_id) + ' not updated.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return False
    log.log('Updated Node ' + str(node_id) + ' to ' + url )
    return True

def delete_node(web_url, node_id):
    '''Delete a node on the web api
    :web_url: Base webaddress of server, or ip
    :node_id: id of node to be deleted on web api
    :returns: boolean of success

    '''
    url = web_url + '/sensors/' + str(node_id)
    try:
        r = requests.delete(url, headers=headers,
                            timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to delete node ' + str(node_id) + '.')
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to delete node ' + str(node_id) + '.')
        return False
    code = r.status_code
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Node ' + str(node_id) + ' not deleted.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        ret = update_headers(web_url)
        if ret:
            return delete_node(web_url, node)
        else:
            return False
    if code == 404:
        # Node not found. Claim deleted internally
        log.log('ERROR: Node ' + str(job_id) + ' not deleted.'
                + ' Server responded with ' + str(code)
                + ' on ' + url)
        log.log('Node wasn\'t found on server to delete'
                + ', faking it deleted')
        return True
    if code != 200:
        log.log('ERROR: Node ' + str(node_id) + ' not deleted.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return False
    log.log('Updated Node ' + str(node_id) + ' to ' + url )
    return True

def add_data(web_url, data, node_id):
    """Adds data to web api
    :web_url: Base webaddress of server, or ip
    :node_id: id of node the data is from
    :data: data to be added to the web api
    :returns: boolean of success

    """
    #TODO sensor data parsing, category will be [temperature,humidity,door], for door send open or closed
    url = web_url + '/sensors/' + node_id + '/data'
    try:
        r = requests.post(url, headers=headers,
                            json=data, timeout=3)
    except requests.ConnectionError:
        log.log('ERROR: Could not connect to ' + url 
                + '. Unable to add data from node ' 
                + str(node_id) + '.')
        return False
    except requests.exceptions.Timeout:
        log.log('ERROR: Timeout when contacting ' + url
                + '. Unable to add data from node '
                + str(node_id) + '.')
        return False
    code = r.status_code
    # Handle error codes from web api
    if code == 401:
        # Not authorized. Fix headers and try again
        log.log('ERROR: Data from node ' + str(node_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        ret = update_headers(web_url)
        return add_data(web_url, printer, node_id)
    if code != 201:
        # Catch all for if bad status codes
        log.log('ERROR: Data from node ' + str(node_id) + ' not added.'
                + ' Server responded with ' + str(code) 
                + ' on ' + url)
        return False
    log.log('Added printer ' + str(node_id) + ' to ' + url )
    return True
