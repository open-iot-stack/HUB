#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests

class WebAPI(object):

    url = None
    key = None
    id  = None
    def __init__(self, url, api_key, log):
        """TODO: Docstring for __init__.

        :url: TODO
        :api_key: TODO
        :hub_id: TODO
        :returns: TODO

        """
        self.url = url
        self.key = api_key
        self.log = log
        self.headers = None

    def sign_in(self):
        #uses api key to get headers for commands, and signs in
        log = self.log
        web_url = self.url
        api_key = self.key
        url =  web_url + '/hub_auth/sign_in'
        headers = { 'Content-Type' : 'application/json',
                'Accept': 'application/json' , 'Authorization': api_key }
        try:
            r = requests.post(url, headers = headers, timeout=10)
        except requests.ConnectionError:
            log.log("ERROR: Could not connect to "
                    + url + ". Trying to sign in.")
            return False
        except requests.exceptions.Timeout:
            log.log("ERROR: Connection timed out with "
                    + url + ". Trying to sign in.")
            return False
        code = r.status_code
        if code == 401:
            log.log("ERROR: Bad status code when signing in. "
                    + str(code)
                    + ". API Key is most likely invalid.")
            return False
        elif code != 200:
            log.log("ERROR: Bad status code when signing in. "
                    + str(code))
            return False
        res_header = r.headers;
        try:
            self.headers = {
                    'access-token' : res_header['access-token'],
                    'uid': res_header['uid'],
                    'token-type': res_header['token-type'],
                    'client' : res_header['client'],
                    'cache-control': "no-cache",
            }
        except KeyError:
            log.log("ERROR: Headers for signin on " 
                    + url + " did not contain necessary information.")
            return False
        data = r.json().get('data')
        self.id = data.get('id')
        return True
            
    def sign_out(self):
        #signs out and invalidates tokens forever
        log = self.log
        web_url = self.url
        api_key = self.key
        headers = self.headers
        url = web_url + '/hub_auth/sign_out'
        try:
                r = requests.delete(url, headers = headers, timeout=10)
        except requests.ConnectionError:
            log.log("ERROR: Could not connect to "
                    + url + ". Trying to sign out.")
            return False
        except requests.exceptions.Timeout:
            log.log("ERROR: Connection timed out with "
                    + url + ". Trying to sign out.")
            return False
        if r.status_code != 200:
            log.log("ERROR: Bad status code when signing out. "
                    + str(code))
            return False
        return True

    def update_headers(self):
        #checks validation and signs in once again
        log = self.log
        web_url = self.url
        api_key = self.key
        #TODO Make sure this doesn't make communication super slow.
        # Might need caching
        if self.headers == None:
            return self.sign_in()
        url = web_url + 'hub_auth/validate_token'
        try:
            r = requests.get(url, headers = self.headers, timeout=10)
        except requests.ConnectionError:
            log.log("ERROR: Could not connect to "
                    + url + ". Trying to validate headers.")
            return False
        except requests.exceptions.Timeout:
            log.log("ERROR: Connection timed out with "
                    + url + ". Trying to validate headers.")
            return False
        code = r.status_code
        if code == 401:
            return self.sign_in()
        elif code != 200:
            log.log("ERROR: Bad status code when validating headers. "
                    + str(code))
            return False
        return True

    def add_printer(self, printer):
        '''Add a printer on the web api
        :web_url: Base webaddress of server, or ip
        :printer: printer to be added to web api
        :returns: webID of printer, None if fails

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
        hub_id = self.id
        printer_id = printer.get('id')
        url = web_url + '/hubs/' + str(hub_id) + '/printers'
        try:
            r = requests.post(url, headers=headers,
                                json=printer, timeout=3)
        except requests.ConnectionError:
            log.log('ERROR: Could not connect to ' + url 
                    + '. Unable to add printer ' 
                    + str(printer_id) + '.')
            return None
        except requests.exceptions.Timeout:
            log.log('ERROR: Timeout when contacting ' + url
                    + '. Unable to add printer '
                    + str(printer_id) + '.')
            return None
        code = r.status_code
        data = r.json()
        # Handle error codes from web api
        if code == 401:
            # Not authorized. Fix headers and try again
            log.log('ERROR: Printer ' + str(printer_id) + ' not added.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            if self.update_headers():
                return self.add_printer(printer)
            return None
        if code != 201:
            # Catch all for if bad status codes
            log.log('ERROR: Printer ' + str(printer_id) + ' not added.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            return None
        webid = data.get('id')
        log.log('Added printer ' + str(printer_id) + ' to ' + url )
        return webid

    def patch_printer(self, printer):
        '''Patch a printer on the web api
        :web_url: Base webaddress of server, or ip
        :printer: printer to be updated on the web api
        :returns: boolean of success

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
        printer_id = printer.get('id')
        url = web_url + '/printers/' + str(printer_id) 
        try:
            r = requests.patch(url, headers=headers,
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
            ret = self.update_headers()
            if ret:
                return self.patch_printer(printer)
            return False
        if code != 200:
            log.log('ERROR: Printer ' + str(printer_id) + ' not updated.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            return False
        log.log('Updated printer ' + str(printer_id) + ' on ' + url )
        return True

    def delete_printer(self, printer_id):
        '''Deletes a printer on the web api
        :web_url: TODO
        :printer_id: TODO
        :returns: TODO

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
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
            ret = self.update_headers()
            if ret:
                return self.delete_printer(printer_id)
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
        

    def add_job(self, job):
        '''Will add a job to the WebAPI.
        Handles errors and logs.
        :web_url: Base webaddress of server, or ip
        :job:     job to be added to web api
        :returns: boolean of success

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
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
            ret = self.update_headers()
            return self.add_job(job)
        if code != 201:
            # Catch all if did not succeed and not handling
            log.log('ERROR: Job ' + str(job_id) + ' not created.'
                    + ' Server responded with ' + str(r.status_code)
                    + ' on ' + url)
            return False
        log.log('Added job ' + str(job_id) + ' to ' + url)
        return True

    def patch_job(self, job):
        '''Will updated a job on the WebAPI.
        Handles errors and logs.
        :web_url: Base webaddress of server, or ip
        :job:     job to be updated on the web api
        :returns: boolean of success

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
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
            ret = self.update_headers()
            if ret:
                return self.patch_job(job)
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
        #log.log('Updated job ' + str(job_id) + ' on ' + url)
        return True

    def delete_job(self, job):
        '''Will delete a job on the WebAPI
        :web_url: Base webaddress of server, or ip
        :job:     job to be deleted to web api
        :returns: boolean of success

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
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
            ret = self.update_headers()
            if ret:
                return self.delete_job(job)
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
        log.log('Deleted job ' + str(job_id) + ' on ' + url)
        return True

    def add_node(self, node):
        '''Add a node to the web api
        :web_url: Base webaddress of server, or ip
        :node: node to be added to web api
        :returns: boolean of success

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
        hub_id = self.id
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
            ret = self.update_headers()
            if ret:
                return self.add_node(node)
            else:
                return False
        if code != 201:
            log.log('ERROR: Node ' + str(node_id) + ' not added.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            return False
        log.log('Added Node ' + str(node_id) + ' to ' + url )
        return True

    def patch_node(self, node):
        '''Patch a node on the web api
        :web_url: Base webaddress of server, or ip
        :node: node to be updated on web api
        :returns: boolean of success

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
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
            ret = self.update_headers()
            if ret:
                return self.patch_node(node)
            else:
                return False
        if code != 200:
            log.log('ERROR: Node ' + str(node_id) + ' not updated.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            return False
        log.log('Updated Node ' + str(node_id) + ' to ' + url )
        return True

    def delete_node(self, node_id):
        '''Delete a node on the web api
        :web_url: Base webaddress of server, or ip
        :node_id: id of node to be deleted on web api
        :returns: boolean of success

        '''
        log = self.log
        headers = self.headers
        web_url = self.url
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
            ret = self.update_headers()
            if ret:
                return self.delete_node(node)
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
        log.log('Deleted Node ' + str(node_id) + ' to ' + url )
        return True

    def add_data(self, data):
        """Adds data to web api
        :web_url: Base webaddress of server, or ip
        :node_id: id of node the data is from
        :data: data to be added to the web api
        :returns: boolean of success

        """
        log = self.log
        headers = self.headers
        web_url = self.url
        id = data.get("id")
        #TODO sensor data parsing, category will be [temperature,humidity,door], for door send open or closed
        url = web_url + '/sensors/' + str(id) + '/data'
        try:
            r = requests.post(url, headers=headers,
                                json=data, timeout=3)
        except requests.ConnectionError:
            log.log('ERROR: Could not connect to ' + url 
                    + '. Unable to add data from sensor ' 
                    + str(id) + '.')
            return False
        except requests.exceptions.Timeout:
            log.log('ERROR: Timeout when contacting ' + url
                    + '. Unable to add data from sensor '
                    + str(id) + '.')
            return False
        code = r.status_code
        # Handle error codes from web api
        if code == 401:
            # Not authorized. Fix headers and try again
            log.log('ERROR: Data from sensor ' + str(id) + ' not added.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            ret = self.update_headers()
            return self.add_data(data)
        if code != 201:
            # Catch all for if bad status codes
            log.log('ERROR: Data from sensor ' + str(id) + ' not added.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            return False
        #log.log('Added data from sensor ' + str(id) + ' to ' + url )
        return True

    def callback_command(self, data):
        """Calls back to the web api for a command that was updated

        :data: TODO
        :returns: TODO

        """
        id      = data.get('id')
        log     = self.log
        headers = self.headers
        web_url = self.url

        url = web_url + "/commands/" + str(id)

        try:
            r = requests.patch(url, headers=headers,
                                json=data, timeout=3)
        except requests.ConnectionError:
            log.log('ERROR: Could not connect to ' + url 
                    + '. Unable to callback command ' 
                    + str(id) + '.')
            return False
        except requests.exceptions.Timeout:
            log.log('ERROR: Timeout when contacting ' + url
                    + '. Unable to callback command '
                    + str(id) + '.')
            return False
        code = r.status_code
        # Handle error codes from web api
        if code == 401:
            # Not authorized. Fix headers and try again
            log.log('ERROR: Callback command '
                    + str(id) + ' not updated.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            ret = self.update_headers()
            return self.callback_command(data)
        if code != 200:
            # Catch all for if bad status codes
            log.log('ERROR: Callback command '
                    + str(id) + ' not updated.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            return False
        log.log('Updated command ' + str(id) + ' on ' + url )
        return True

    def update_nodes(self, data):
        """Updates the list of nodes on the web api
        :returns: boolean of success

        """
        id      = self.id
        log     = self.log
        headers = self.headers
        web_url = self.url
        data["status"] = "online"

        url = web_url + "/hubs/" + str(id)
        try:
            r = requests.patch(url, headers=headers,
                                json=data, timeout=3)
        except requests.ConnectionError:
            log.log('ERROR: Could not connect to ' + url 
                    + '. Unable to update nodes on hub ' 
                    + str(id) + '.')
            return False
        except requests.exceptions.Timeout:
            log.log('ERROR: Timeout when contacting ' + url
                    + '. Unable to update nodes on hub '
                    + str(id) + '.')
            return False
        code = r.status_code
        # Handle error codes from web api
        if code == 401:
            # Not authorized. Fix headers and try again
            log.log('ERROR: Node update for hub '
                    + str(id) + ' not updated.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            ret = self.update_headers()
            return self.callback_command(data)
        if code != 200:
            # Catch all for if bad status codes
            log.log('ERROR: Node update for hub '
                    + str(id) + ' not updated.'
                    + ' Server responded with ' + str(code) 
                    + ' on ' + url)
            return False
        log.log('Updated nodes for hub ' + str(id) + ' on ' + url )
        return True
