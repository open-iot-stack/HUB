from flask import Flask

app = Flask(__name__)

import hub.printers
import hub.Server
