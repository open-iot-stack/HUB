#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hub
import sys
import getopt
import thread
import hub.models
from hub import app
from hub.dealer import data_receiver
from hub.logger import Log

from hub.database import init_db

debug         = False
port          = None
host          = None
threaded      = False
print_enabled = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "hdtvp:a:",
            ["apikey=","pass=","help",
                "port=","debug","host=",
                "threaded","verbose"])
except getopt.GetoptError, err:
    # Print debug info
    print str(err)
    sys.exit(2)

for opt, arg in opts:
    if opt in ["-h", "--help"]:
        print "Usage: Server.py"\
        + "\n    -a/--apikey <apikey>"\
        + "\n    -p/--port   <port>"\
        + "\n       --pass   <password>"\
        + "\n       --host   <ip address>"\
        + "\n    -d/--debug"\
        + "\n    -h/--help"\
        + "\n    -t/--threaded"\
        + "\n    -v/--verbose"
        sys.exit(0)
    elif opt in ["-a", "--apikey"]:
        hub.API_KEY = arg
    elif opt in ["--pass"]:
        hub.SND_PASSWD = arg
    elif opt in ["-p", "--port"]:
        port = int(arg)
    elif opt in ["-d", "--debug"]:
        debug = True
    elif opt in ["--host"]:
        host = arg
    elif opt in ["-t", "--threaded"]:
        threaded = True
    elif opt in ["-v", "--verbose"]:
        print_enabled = True

hub.log = Log(print_enabled=print_enabled)

thread.start_new_thread(data_receiver, ())
init_db()
app.run(host=host, debug=debug, port=port,threaded=threaded)

