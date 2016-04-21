from flask import Flask
from hub.config import Config
from hub.channel import Channel
from hub.logger import Log
import hub.auth

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads/"

import hub.printers
import hub.nodes
import hub.base

conf = Config()
send_channel, recv_channel = Channel()

# These all get defined from commandline args
log        = None
SND_PASSWD = None
API_KEY    = None
WEB_API    = hub.auth.dev_url
