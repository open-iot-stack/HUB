#!octopifunctions.py (I don't know where this will be in the hub)

###############################################
#   Author: Aaron Preston
#   Email: aaronpre@buffalo.edu
#   Status: In Development
#   Last Revision Date: 4/1/16
###############################################
# See this for documentation: http://docs.octoprint.org/en/master/api/fileops.html

import json
import os
import httplib
import requests


##################################### TESTING CODE (DELETE FOR RELEASE) #####################################

#Function Header Template:
###############################################
#   Function Name:
#   Function Description:
#   Parameter [0]:
#   Paramter [...n]:
#   retVal: On Success:
#           On Fail:
###############################################

testingOctopiUrl = '169.254.212.2'
testingApiKey = '059936A9790743DD8E13632F9ECE9C24'
testingWebcamStreamURL = '/webcam/?action=stream'

# Constants:
type_get = 'GET'
type_put = 'PUT'
type_post = 'POST'
type_delete = 'DELETE'
files_local_extension = '/api/files/local'
files_sd_extension = '/api/files/sdcard'
local = '/local'
files_extension = '/api/files'
printer_extension = '/api/printer'
jobs_extension = '/api/job'
version_extension = '/api/version'
printer_profile_extension = '/api/printerprofiles'
slicer_profile_extension = '/api/slicing/cura/profiles' #Note: normally, slicer profiles are organized per Slicer but the octopi only has one Slicer (cura)
#    File API Calls:
#        Retrieve all files
#        Retrieve files from specific location
#        Upload a file
#        Retrieve a file's information
#        Issue a command:
#           'command':'target'
#           'command':'offset'
#        Delete a file
#   Job API Calls:
#       Issue A command:
#           'command':'start'
#           'command':'restart'
#           'command':'pause'
#           'command':'cancel'
#       Retrieve Job information
#   Printer API Calls:
#       Retrieve Printer (all, unless excluded) States
#       Issue Print Head Command:
#           'command':'jog'
#           'command':'home'
#           'command':'feedrate'
#       Issue Tool Command:
#           'command':'target'
#           'command':'offset'
#           'command':'select'
#           'command':'extrude'
#           'command':'flowrate'
#       Retrieve Tool State
#       Issue Bed Command:
#           'command':'target'
#           'command':'offset'
#       Issue SD Command:
#           'command':'init'
#           'command':'refresh'
#           'command':'release'
#       Retrieve SD State 
#   Printer Profile API Calls:
#       Retrieve all Printer Profiles
#       Add new Printer Profile
#       Update a Printer Profile
#       Remove a Printer Profile
#   Slicing API Calls: *Note: normally, clicer profiles are organized per Slicer but the octopi only has one Slicer
#       Get All Slicers and Slicer Profiles
#       Retrieve Specific Slicer Profile
#       Add Slicer Profile
#       Delete Slicer Profile

##################################### END TESTING CODE #####################################


##################################### PRIVATE METHODS #####################################

 #########################################################################
#   Function Name: http_request
#   Function Description:
#       -Calls sends (any) http request to The octopi
#   Parameter [0]: url_address {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiExtension {string} URL to be added to url_address 
#        ex) '/api/files'
#   Parameter [2]: params {dict} parameters passed into HTTP request
#        ex) {'file': file_to_upload, 'print':True}
#   Parameter [3]: httpMethod {string} type of HTTP request, passed into HTTP request
#        ex) 'GET'
#   Parameter [4]: header {dict} header for HTTP request, passed into HTTP request
#        ex) {'Host': 'example.com', 'X-Api-Key': api_key}
#   retVal: if successful request, then the response body (Exception: status 204, which has no content)
#           if unsuccessful request, then the response code and response reason
 #########################################################################
def http_request(address, api_extension,
        method, headers, params=None,  files=None, json=None, data=None):
    url = "http://" + address + api_extension
    try:
        if method == type_get:
            response = requests.get(url, headers=headers, params=params)
        elif method == type_post:
            response = requests.post(url, headers=headers, params=params,
                                        files=files, json=json, data=data)
    except requests.ConnectionError:
        hub.log.log("ERROR: Could not connect to " + url)
        return None
    except requests.exceptions.Timeout:
        hub.log.log("ERROR: Timeout occured on " + url)
        return None
    return response

########################
    conn = httplib.HTTPConnection(url_address)
    conn.request(httpMethod, apiExtension, str(params), header)
    response = conn.getresponse()
    return response
    if(200 <=  response.status and response.status < 300):
        if response.status is 204: #delete returns no content and crashes 
            return response.status
        else :
            return json.loads(response.read())
    else:
        return str(response.status) + '\n' + str(response.reason)   
    
    
##################################### PUBLIC METHODS #####################################

    
############################ FILE OPERATIONS #################################


 #########################################################################
#   Function Name: GetAllFiles
#   Function Description:
#       -Creates http request to The octopi to view all files
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the http_request, On success, it returns the files
#       On fail, it returns the response code and response reason
 #########################################################################
def get_all_files(url, api_key):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    return http_request(url, files_extension, type_get, header)
 
 
 #########################################################################
#   Function Name: GetAllFilesFromLocation
#   Function Description:
#       -Creates http request to The octopi to view all files in a directory
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path on the Octopi leading to a directory of files
#        ex) '/local/4_1_16'
#   retVal: result of the http_request, On success, it returns the files
#       On fail, it returns the response code and response reason
 #########################################################################
def get_all_files_from_location(url, api_key, path = local):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    return http_request(url, files_extension + path, type_get, header)
       

 #########################################################################
#   Function Name: upload_file
#   Function Description:
#       -Uploads a File to either the Octopi, or the SD in the Printer
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: file_path {string} path of file to upload
#        ex) 'C:/Users/aaron/Projects/cotopi/rpi2-bottom_8020_netfabb.stl'
#   Parameter [3]: path_to_store {string} path on the Octopi (or 3d printer) where the upload will be saved
#        ex) '/local/4_1_16'
#   retVal: result of the http_request, On success, it returns a response with a "location" header set to the url of the uploaded file.
#       On fail, it returns the response code and response reason
 #########################################################################
def upload_file(url, api_key, file_path, path_to_store = local):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    fname = os.path.basename(file_path)
    file_to_upload =  open(file_path, 'rb')
    files = {'file': (fname, file_to_upload, 'application/octet-stream')}
    params = {
        'print':'false',
    }
    return http_request(url, files_extension + path_to_store, type_post, header,
                            params=params, files=files) 
    
def upload_file_and_select(url, api_key, file_path, path_to_store = local):
    """uploads a file to the octopi and selects it"""
    header = {'Host': 'example.com', 'X-Api-Key': api_key}
    data   = {'select': 'true'}
    file_to_upload = open(file_path, 'rb')
    files = {'file': (fname, file_to_upload, 'application/octet-stream')}
    return http_request(url, files_extension + path_to_store, type_post, header,
                            files=files, data=data)
    
 #########################################################################
#   Function Name: upload_file_and_print
#   Function Description:
#       -Uploads a File to either the Octopi, or the SD in the Printer, then selects the file and prints it 
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: file_path {string} path of file to upload
#        ex) 'C:/Users/aaron/Projects/cotopi/rpi2-bottom_8020_netfabb.stl'
#   Parameter [3]: path_to_store {string} path on the Octopi (or 3d printer) where the upload will be saved
#        ex) '/local/4_1_16'
#   retVal: result of the http_request, On success, it returns a response with a "location" header set to the url of the uploaded file.
#       On fail, it returns the response code and response reason
 #########################################################################
def upload_file_and_print(url, api_key, file_path, path_to_store = local):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    file_to_upload =  open(file_path, 'rb')
    files = {'file': (fname, file_to_upload, 'application/octet-stream')}
    data = {'print': "true"}
    return http_request(url, files_extension +path_to_store, type_post, header,
                            data=data, files=files) 
    
 #########################################################################
#   Function Name: get_one_file_info
#   Function Description:
#       -Retrieves information of a file
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to view
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the http_request, On success, the file's information.
#       On fail, it returns the response code and response reason
 #########################################################################
def get_one_file_info(url, api_key, path = local): 
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    return http_request(url, files_extension + path, type_get, header)     
    
    
 #########################################################################
#   Function Name: delete_file
#   Function Description:
#       -deletes a file on the octopi (or sd card in the 3D printer)
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the http_request, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################
def delete_file(url, api_key, path):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}    
    return http_request(url, files_extension + path, type_delete, header)
    
    
 #########################################################################
#   Function Name: command_select
#   Function Description:
#       -Selects a file on the octopi (or sd card in the 3D printer)
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the http_request, On success, returns response status 200 
#       On fail, it returns the response code and response reason
 #########################################################################  
def command_select(url, api_key, path):
    header = { 
            'Host': 'example.com',
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
    }
    payload = {
            'command': 'select',
            'print': 'false'
    }
    return http_request(url, files_extension + path, type_post, header,
                            json=payload)


 #########################################################################
#   Function Name: command_select_and_print
#   Function Description:
#       -Selects a file on the octopi (or sd card in the 3D printer) and then prints it
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the http_request, On success, returns response status 200 
#       On fail, it returns the response code and response reason
 #########################################################################  
def command_select_and_print(url, api_key, path):
    header = {
        'Host': 'example.com',
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'command': 'select',
        'print': 'true'
    }
    params = json.dumps(data)
    return http_request(url, files_extension + path, type_post, header,
                            data=data)
    
    
 #########################################################################
#   Function Name: command_slice
#   Function Description:
#       -Creates a .gcode (sliced) file of the selected file on the octopi (or sd card in the 3D printer)
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the http_request, On success, returns response status 202 
#       On fail, it returns the response code and response reason
 #########################################################################  
def command_slice(url, api_key, file_name, path_to_store = local):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key, 'Content-Type': 'application/json'}
    #fileName = os.path.basename(path)
    #fileNameNoExt = os.path.splitext(fileName)[0]
    endpoint = files_extension + path_to_store + "/" + file_name
    payload = {
        'command': 'slice'
    }
    #data ['command'] = 'slice'
    #data ['slicer'] = 'cura'
    #data ['gcode'] = fileNameNoExt + '.gcode'
    #data ['printerProfile'] = '<printer profile name>'
    #data ['profile'] = '<profile name>'
    #data ['profile.infill'] = 75
    #data ['profile.density'] = 15
    #data ['position'] = {'x':100, 'y':100}
    ##[OPTIONAL]
    #data ['select'] = False
    ##[OPTIONAL]
    #data ['print'] = False
    
    return http_request(url, endpoint, type_post, header,
                            json=payload)

############################ JOB OPERATIONS #################################


 #########################################################################
#   Function Name: start_command
#   Function Description:
#       -Starts the print of the currently selected file. if no file is selected, this will return 409
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the http_request, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################  
def start_command(url, api_key):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key, 'Content-Type': 'application/json'}
    payload = {'command': 'start'}
    return http_request(url, jobs_extension, type_post, header,
                            json=payload)
    
    
 #########################################################################
#   Function Name: restart_command
#   Function Description:
#       -Restarts the print of the currently selected file And active (Paused) print job.
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the http_request, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################  
def restart_command(url, api_key):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key, 'Content-Type': 'application/json'}
    payload = {'command': 'restart'}
    return http_request(url, jobs_extension, type_post, header,
                            json=payload)

    
 #########################################################################
#   Function Name: PauseCommand
#   Function Description:
#       -Pauses/Unpauses current print job. If no active job, then 409 will be returned
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the http_request, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################      
def pause_unpause_command(url, api_key):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key, 'Content-Type': 'application/json'}
    payload = {'command': 'pause'}
    return http_request(url, jobs_extension, type_post, header,
                            json=payload)
    
    
 #########################################################################
#   Function Name: cancel_command
#   Function Description:
#       -Cancels current print job. If no active job, then 409 will be returned
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the http_request, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################     
def cancel_command(url, api_key):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key, 'Content-Type': 'application/json'}
    payload = {'command': 'cancel'}
    return http_request(url, jobs_extension, type_post, header, 
                            json=payload)

            
 #########################################################################
#   Function Name: get_job_info
#   Function Description:
#       -Get information about the current print job.
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: api_key {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: *NOTE this will always return 200 and response (even if there isn't a printer connected)
 #########################################################################  
def get_job_info(url, api_key):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    return http_request(url, jobs_extension, type_get, header) 
    
def get_printer_info(url, api_key):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    params = {"exclude": "temperature,sd"}
    return http_request(url, printer_extension, type_get, header,
                            params=params)

def slice_and_print(url, api_key, file_name, path_to_store = local):
    header = { 'Host': 'example.com', 'X-Api-Key': api_key}
    #file_name = os.path.basename(path)
    endpoint = files_extension + path_to_store + "/" + file_name
    payload = {
            'command': 'slice',
            'print': 'true'
    }
    return http_request(url, endpoint, type_post, header,
                            json=payload)

def get_version(url, api_key):
    headers = {'Host': 'example.com', 'X-Api-Key': api_key}
    return http_request(url, version_extension, type_get, headers)







if __name__ == "__main__":
##################################### DELETE THESE, ONLY USED FOR TESTING #####################################

    print '\n'
#this is an stl file that will be used to test printing through the octopi
    pathToFile = 'C:\\Users\\aaron\\Projects\\octopi\\rpi2-bottom_8020_netfabb.stl'
#print 'Valid filepath? -' + str(os.path.isfile(pathToFile))
    dumbPathFile = 'pathto/here/filename.c'
    pathToSampleStl = local + '/rpi2-bottom_8020_netfabb.stl'

############################ TESTING FILE OPERATIONS #################################


###################### THIS IS WORKING 
#print 'testing GetAllFiles:'
#print GetAllFiles(testingOctopiUrl, testingApiKey)
#print '\n'

###################### THIS IS WORKING 
#print 'testing GetAllFilesFromLocation:'
#print GetAllFilesFromLocation(testingOctopiUrl, testingApiKey)
#print '\n'

##################### RECIEVING 400 : bad request
    print 'testing upload_file:'
    print upload_file(testingOctopiUrl, testingApiKey, pathToFile)
    print '\n'

##################### RECIEVING 400 : bad request
    print 'testing upload_file_and_print:'
    print upload_file_and_print(testingOctopiUrl, testingApiKey, pathToFile, local)
    print '\n'

###################### THIS IS WORKING 
#print 'testing GetonOneFileInfo:'
#print get_one_file_info(testingOctopiUrl, testingApiKey, local + '/rpi2-bottom_8020_netfabb.stl')
#print '\n'

###################### THIS IS WORKING 
#print 'testing delete_file:'
#print delete_file(testingOctopiUrl, testingApiKey, local + '/rpi2-bottom_8020_netfabb.stl')
#print '\n'

###################### THIS IS WORKING 
#print 'testing command_select:'
#print command_select(testingOctopiUrl, testingApiKey, )
#print '\n'
    
###################### THIS IS WORKING 
#print 'testing command_select_and_print:'
#print command_select(testingOctopiUrl, testingApiKey, pathToSampleStl)
#print '\n'
    
##################### NEEDS FUTHER TESTING ############# May need a slicer? getting 405, method not allowed
    print 'testing command_slice:'
    print command_slice(testingOctopiUrl, testingApiKey, pathToSampleStl)
    print '\n'


############################ TESTING JOB OPERATIONS #################################


##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
    print 'testing Start Command:'
    print start_command(testingOctopiUrl, testingApiKey)
    print '\n'

##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
    print 'testing Pause Command:'
    print PauseCommand(testingOctopiUrl, testingApiKey)
    print '\n'

##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
    print 'testing Restart Command:'
    print restart_command(testingOctopiUrl, testingApiKey)
    print '\n'

##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
    print 'testing Cancel Command:'
    print cancel_command(testingOctopiUrl, testingApiKey)
    print '\n'

###################### THIS IS WORKING 
#print 'testing Get Job Info:'
#print get_job_info(testingOctopiUrl, testingApiKey)
#print '\n'
