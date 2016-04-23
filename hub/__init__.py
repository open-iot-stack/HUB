from flask import Flask
from hub.config import Config
from hub.channel import Channel
from hub.logger import Log
from hub.db_wrapper import Printers

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads/"

import hub.printers
import hub.nodes
import hub.base
import hub.auth

printers_wrapper = Printers()
conf = Config()
send_channel, recv_channel = Channel()

# These all get defined from commandline args
log        = None
SND_PASSWD = None
API_KEY    = None
WEB_API    = hub.auth.dev_url
ID         = 0
#TODO get correct ID
