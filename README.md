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
<p>clone this repo to where you see fit, for example: /home/$USER/git/</p>
<p>run install.py as root</p>
<p>Options:</p>
<p>    --Config File:</p>
<p>        The name of the file that the configuration settings should be saved. (arguments.config by default)</p>
<p>    --Web API URL:</p>
<p>        URL of the Web API. (https://dev.api.stratusprint.com/v1 by default)</p>
<p>    --Web API Key:</p>
<p>        The API Key for the hub assigned by the Web Control Panel. Is needed to update the Web Control Panel.</p>
<p>    --Access Point SSID:</p>
<p>        The SSID for the Wireless Access Point. (StratusPrint by default)</p>
<p>    --Access Point Password:</p>
<p>        The Password for the Wireless Access Point.</p>
<p>    --Interface:</p>
<p>        The interface to run the Wireless Access Point on. (wlan0 by default)</p>
<p>    --Interface IP:</p>
<p>        The IP Address for the interface to run on. This will be the HUB IP for nodes and printers. (192.168.0.1 by default)</p>
<p>    --Port:</p>
<p>        The Port for Flask to run on. Should not be run on 80, use a proxy if using 80. (5000 by default)</p>
<p>    --Host:</p>
<p>        The IP Address for Flask to listen on. (0.0.0.0 by default, this will cause it to run on all IP's)</p>

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
