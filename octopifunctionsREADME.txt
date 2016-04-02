octopifunctions.py


Go To OctoPi for refernce:  http://docs.octoprint.org/en/master/api/fileops.html

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

 
 #############################################################################
 ############################ FILE OPERATIONS #################################
 #############################################################################

 
 
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

 
 #############################################################################
 ############################ JOB OPERATIONS #################################
 #############################################################################

 
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

 
 
 
 
 
 
 
 
 
 
 
 