# HUB
Communication layer for peripherals and web-api

##Installation
###Prerequisites
####Currently installation is configured for systemd only, which is enabled in the latest version of raspbian
####Packages:
<p>dnsmasq</p>
hostapd</p>
<p>    --install these through your distro's package manager</p>
###Configuration
####Steps
clone this repo to where you see fit, for example: /home/$USER/git/
<br>run install.py as root
<br>Options:
#####--Config File:
The name of the file that the configuration settings should be saved. (arguments.config by default)
#####--Web API URL:
URL of the Web API. (https://dev.api.stratusprint.com/v1 by default)
#####--Web API Key:
The API Key for the hub assigned by the Web Control Panel. Is needed to update the Web Control Panel.
#####--Access Point SSID:
The SSID for the Wireless Access Point. (StratusPrint by default)
#####--Access Point Password:
The Password for the Wireless Access Point.
#####--Interface:
The interface to run the Wireless Access Point on. (wlan0 by default)
#####--Interface IP:
The IP Address for the interface to run on. This will be the HUB IP for nodes and printers. (192.168.0.1 by default)
#####--Port:
The Port for Flask to run on. Should not be run on 80, use a proxy if using 80. (5000 by default)
#####--Host:
The IP Address for Flask to listen on. (0.0.0.0 by default, this will cause it to run on all IP's)

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
