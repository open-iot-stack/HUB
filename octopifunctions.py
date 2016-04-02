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
typeGet = 'GET'
typePut = 'PUT'
typePost = 'POST'
typeDelete = 'DELETE'
filesLocalExtension = '/api/files/local'
filesSDExtension = '/api/files/sdcard'
local = '/local'
filesExtension = '/api/files'
printerExtension = '/api/priner'
jobsExtension = '/api/job'
printerProfileExtension = '/api/printerprofiles'
slicerProfileExtension = '/api/slicing/cura/profiles' #Note: normally, slicer profiles are organized per Slicer but the octopi only has one Slicer (cura)
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
#   Function Name: HttpRequest
#   Function Description:
#       -Calls sends (any) http request to The octopi
#   Parameter [0]: urlAddress {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiExtension {string} URL to be added to urlAddress 
#        ex) '/api/files'
#   Parameter [2]: params {dict} parameters passed into HTTP request
#        ex) {'file': fileToUpload, 'print':True}
#   Parameter [3]: httpMethod {string} type of HTTP request, passed into HTTP request
#        ex) 'GET'
#   Parameter [4]: header {dict} header for HTTP request, passed into HTTP request
#        ex) {'Host': 'example.com', 'X-Api-Key': apiKey}
#   retVal: if successful request, then the response body (Exception: status 204, which has no content)
#           if unsuccessful request, then the response code and response reason
 #########################################################################
def HttpRequest(urlAddress, apiExtension, params, httpMethod, header):
    conn = httplib.HTTPConnection(urlAddress)
    conn.request(httpMethod, apiExtension, str(params), header)
    response = conn.getresponse()
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
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the HttpRequest, On success, it returns the files
#       On fail, it returns the response code and response reason
 #########################################################################
def GetAllFiles(url, apiKey):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey}
    return HttpRequest(url, filesExtension, None, typeGet, header)
 
 
 #########################################################################
#   Function Name: GetAllFilesFromLocation
#   Function Description:
#       -Creates http request to The octopi to view all files in a directory
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path on the Octopi leading to a directory of files
#        ex) '/local/4_1_16'
#   retVal: result of the HttpRequest, On success, it returns the files
#       On fail, it returns the response code and response reason
 #########################################################################
def GetAllFilesFromLocation(url, apiKey, path = local):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey}
    return HttpRequest(url, filesExtension + path, None, typeGet, header)
       

 #########################################################################
#   Function Name: UploadFile
#   Function Description:
#       -Uploads a File to either the Octopi, or the SD in the Printer
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: filePath {string} path of file to upload
#        ex) 'C:/Users/aaron/Projects/cotopi/rpi2-bottom_8020_netfabb.stl'
#   Parameter [3]: pathToStore {string} path on the Octopi (or 3d printer) where the upload will be saved
#        ex) '/local/4_1_16'
#   retVal: result of the HttpRequest, On success, it returns a response with a "location" header set to the url of the uploaded file.
#       On fail, it returns the response code and response reason
 #########################################################################
def UploadFile(url, apiKey, filePath, pathToStore = local):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/vnd.ms-pkistl'}
    fileToUpload =  open(filePath, 'rb')
    params = {'file': fileToUpload, 'print':False}
    return HttpRequest(url, filesExtension + pathToStore, params, typePost, header) 
    
    
 #########################################################################
#   Function Name: UploadFileAndPrint
#   Function Description:
#       -Uploads a File to either the Octopi, or the SD in the Printer, then selects the file and prints it 
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: filePath {string} path of file to upload
#        ex) 'C:/Users/aaron/Projects/cotopi/rpi2-bottom_8020_netfabb.stl'
#   Parameter [3]: pathToStore {string} path on the Octopi (or 3d printer) where the upload will be saved
#        ex) '/local/4_1_16'
#   retVal: result of the HttpRequest, On success, it returns a response with a "location" header set to the url of the uploaded file.
#       On fail, it returns the response code and response reason
 #########################################################################
def UploadFileAndPrint(url, apiKey, filePath, pathToStore = local):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey}
    fileToUpload =  open(filePath, 'rb')
    params = {'file': fileToUpload, 'print':True}
    return HttpRequest(url, filesExtension +pathToStore, params, typePost, header) 
    
 #########################################################################
#   Function Name: GetOneFileInfo
#   Function Description:
#       -Retrieves information of a file
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to view
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the HttpRequest, On success, the file's information.
#       On fail, it returns the response code and response reason
 #########################################################################
def GetOneFileInfo(url, apiKey, path = local): 
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey}
    return HttpRequest(url, filesExtension + path, None, typeGet, header)     
    
    
 #########################################################################
#   Function Name: DeleteFile
#   Function Description:
#       -deletes a file on the octopi (or sd card in the 3D printer)
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the HttpRequest, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################
def DeleteFile(url, apiKey, path):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey}    
    return HttpRequest(url, filesExtension + path, None, typeDelete, header)
    
    
 #########################################################################
#   Function Name: CommandSelect
#   Function Description:
#       -Selects a file on the octopi (or sd card in the 3D printer)
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the HttpRequest, On success, returns response status 200 
#       On fail, it returns the response code and response reason
 #########################################################################  
def CommandSelect(url, apiKey, path):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/json'}
    data = {}
    data ['command'] = 'select'
    data ['print'] = False
    params = json.dumps(data)
    return HttpRequest(url, filesExtension + path, params, typePost, header)


 #########################################################################
#   Function Name: CommandSelectAndPrint
#   Function Description:
#       -Selects a file on the octopi (or sd card in the 3D printer) and then prints it
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the HttpRequest, On success, returns response status 200 
#       On fail, it returns the response code and response reason
 #########################################################################  
def CommandSelectAndPrint(url, apiKey, path):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/json'}
    data = {}
    data ['command'] = 'select'
    data ['print'] = True
    params = json.dumps(data)
    return HttpRequest(url, filesExtension + path, params, typePost, header)
    
    
 #########################################################################
#   Function Name: CommandSlice
#   Function Description:
#       -Creates a .gcode (sliced) file of the selected file on the octopi (or sd card in the 3D printer)
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   Parameter [2]: path {string} path of file to delete
#        ex) '/local/4_1_16/rpi_case.stl'
#   retVal: result of the HttpRequest, On success, returns response status 202 
#       On fail, it returns the response code and response reason
 #########################################################################  
def CommandSlice(url, apiKey, path):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/json'}
    fileName = os.path.basename(path)
    fileNameNoExt = os.path.splitext(fileName)[0]
    data = {}
    data ['command'] = 'slice'
    data ['slicer'] = 'cura'
    data ['gcode'] = fileNameNoExt + '.gcode'
    data ['printerProfile'] = '<printer profile name>'
    data ['profile'] = '<profile name>'
    data ['profile.infill'] = 75
    data ['profile.density'] = 15
    data ['position'] = {'x':100, 'y':100}
    #[OPTIONAL]
    data ['select'] = False
    #[OPTIONAL]
    data ['print'] = False
    
    params = json.dumps(data)
    
    return HttpRequest(url, filesExtension, params, typePost, header)

############################ JOB OPERATIONS #################################


 #########################################################################
#   Function Name: StartCommand
#   Function Description:
#       -Starts the print of the currently selected file. if no file is selected, this will return 409
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the HttpRequest, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################  
def StartCommand(url, apiKey):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/json'}
    params = {'command': 'start'}
    return HttpRequest(url, jobsExtension, params, typePost, header)
    
    
 #########################################################################
#   Function Name: RestartCommand
#   Function Description:
#       -Restarts the print of the currently selected file And active (Paused) print job.
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the HttpRequest, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################  
def RestartCommand(url, apiKey):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/json'}
    params = {'command': 'restart'}
    return HttpRequest(url, jobsExtension, params, typePost, header)

    
 #########################################################################
#   Function Name: PauseCommand
#   Function Description:
#       -Pauses/Unpauses current print job. If no active job, then 409 will be returned
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the HttpRequest, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################      
def PauseUnpauseCommand(url, apiKey):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/json'}
    params = {'command': 'pause'}
    return HttpRequest(url, jobsExtension, params, typePost, header)
    
    
 #########################################################################
#   Function Name: CancelCommand
#   Function Description:
#       -Cancels current print job. If no active job, then 409 will be returned
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: result of the HttpRequest, On success, returns response status 204 (no content)
#       On fail, it returns the response code and response reason
 #########################################################################     
def CancelCommand(url, apiKey):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey, 'Content-Type': 'application/json'}
    params = {'command': 'cancel'}
    return HttpRequest(url, jobsExtension, params, typePost, header)

            
 #########################################################################
#   Function Name: GetJobInfo
#   Function Description:
#       -Get information about the current print job.
#   Parameter [0]: url {string} URL of pi 
#        ex) '169.254.212.2'
#   Parameter [1]: apiKey {string} API key required to use the Octopi's REST API
#        ex) '059936A9790743DD8E13632F9ECE9C24'
#   retVal: *NOTE this will always return 200 and response (even if there isn't a printer connected)
 #########################################################################  
def GetJobInfo(url, apiKey):
    header = { 'Host': 'example.com', 'X-Api-Key': apiKey}
    return HttpRequest(url, jobsExtension, None, typeGet, header) 
    









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
print 'testing UploadFile:'
print UploadFile(testingOctopiUrl, testingApiKey, pathToFile)
print '\n'

##################### RECIEVING 400 : bad request
print 'testing UploadFileAndPrint:'
print UploadFileAndPrint(testingOctopiUrl, testingApiKey, pathToFile, local)
print '\n'

###################### THIS IS WORKING 
#print 'testing GetonOneFileInfo:'
#print GetOneFileInfo(testingOctopiUrl, testingApiKey, local + '/rpi2-bottom_8020_netfabb.stl')
#print '\n'

###################### THIS IS WORKING 
#print 'testing DeleteFile:'
#print DeleteFile(testingOctopiUrl, testingApiKey, local + '/rpi2-bottom_8020_netfabb.stl')
#print '\n'

###################### THIS IS WORKING 
#print 'testing CommandSelect:'
#print CommandSelect(testingOctopiUrl, testingApiKey, )
#print '\n'
    
###################### THIS IS WORKING 
#print 'testing CommandSelectAndPrint:'
#print CommandSelect(testingOctopiUrl, testingApiKey, pathToSampleStl)
#print '\n'
    
##################### NEEDS FUTHER TESTING ############# May need a slicer? getting 405, method not allowed
print 'testing CommandSlice:'
print CommandSlice(testingOctopiUrl, testingApiKey, pathToSampleStl)
print '\n'


############################ TESTING JOB OPERATIONS #################################


##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
print 'testing Start Command:'
print StartCommand(testingOctopiUrl, testingApiKey)
print '\n'

##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
print 'testing Pause Command:'
print PauseCommand(testingOctopiUrl, testingApiKey)
print '\n'

##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
print 'testing Restart Command:'
print RestartCommand(testingOctopiUrl, testingApiKey)
print '\n'

##################### NEEDS FUTHER TESTING ############# NEEDS A PRINTER!
print 'testing Cancel Command:'
print CancelCommand(testingOctopiUrl, testingApiKey)
print '\n'

###################### THIS IS WORKING 
#print 'testing Get Job Info:'
#print GetJobInfo(testingOctopiUrl, testingApiKey)
#print '\n'