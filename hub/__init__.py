from flask import Flask, json
from hub.config import Config
from hub.channel import Channel
from hub.logger import Log
from hub.listener import Listener
from hub.webapi import WebAPI


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads/"

import hub.printers
import hub.nodes
import hub.base

printer_listeners = Listener()
node_listeners    = Listener()
conf = Config()

# These all get defined from commandline args
log         = None
SND_PASSWD  = None
WEB_API_KEY = None
WEB_API_URL = 'https://dev.api.stratusprint.com/v1'
ID         = 0
Webapi = None
#TODO get correct ID

