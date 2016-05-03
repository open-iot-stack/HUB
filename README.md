# HUB
Communication layer for peripherals and web-api

##Starting Server
###Arguments
####-c/--config arguments.config
Load a config file instead along with command line arguments. See arguments.config as an example, modify as needed
####-w/--weburl 'http://...'
Set the URL for contacting the WebAPI
####-a/--apikey key
Set the API key to use when contacting the WebAPI
####-p/--port port
Set the port for Flask to run on
####-d/--debug
Run Flask in debug mode
####-t/--threaded
Run Flask in threaded mode (recommended)
####-v/--verbose
Run in verbose mode, all logging will be printed to stdout as well as the output from Flask
