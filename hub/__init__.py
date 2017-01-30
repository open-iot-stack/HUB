from flask import Flask, json
from hub.config import Config
from hub.logger import Log
from hub.listener import Listener


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads/"

import hub.printers
import hub.nodes
import hub.base
import hub.wink

printer_listeners = Listener()
node_listeners    = Listener()
conf = Config()

# These all get defined from commandline args
log         = None
SND_PASSWD  = None
WEB_API_KEY = None
WEB_API_URL = 'https://home.nolanfoster.me/v1'
ID         = 0
Webapi = None
#TODO get correct ID

