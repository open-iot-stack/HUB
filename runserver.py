#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, hub, sys, getopt, _thread
from hub import app
from hub.logger import Log
from hub.webapi import WebAPI
from hub.models import Printer, Node, Account
from hub.dealer import PrinterCollector, NodeCollector
from hub.database import init_db
from hub import wink

debug         = False
port          = None
host          = None
threaded      = False
print_enabled = False
config        = None

def set_args(args):
    global hub
    global config
    global debug
    global host
    global threaded
    global port
    global print_enabled
    try:
        opts, args = getopt.getopt(args, "hdtvp:a:w:c:",
                ["apikey=","pass=","help",
                    "port=","debug","host=",
                    "threaded","verbose","weburl=",
                    "config="])
    except getopt.GetoptError as err:
        # Print debug info
        print (str(err))
        sys.exit(2)
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print ("Usage: Server.py"\
            + "\n    -c/--config <arguments.config file>"\
            + "\n           load config file for arguments. "\
            + "\n           each argument on it's own line"\
            + "\n           with a space between option and argument"\
            + "\n    -w/--weburl <web url>"\
            + "\n    -a/--apikey <apikey>"\
            + "\n    -p/--port   <port>"\
            + "\n       --pass   <password>"\
            + "\n       --host   <ip address>"\
            + "\n    -d/--debug"\
            + "\n    -h/--help"\
            + "\n    -t/--threaded"\
            + "\n    -v/--verbose")
            sys.exit(0)
        elif opt in ["-c", "--config"]:
            config = arg
        elif opt in ["-w", "--weburl"]:
            hub.WEB_API_URL = arg
        elif opt in ["-a", "--apikey"]:
            hub.WEB_API_KEY = arg
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

def load_config(config):
    path = os.path.abspath(config)
    l = []
    with open(path, "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            l.extend(line.split())
    set_args(l)
    return 0

set_args(sys.argv[1:])
if config != None:
    load_config(config)

hub.log = Log(print_enabled=print_enabled)
hub.log.log("Starting up HUB webserver")

init_db()
updates = {"nodes": []}
node_updates = updates.get("nodes")

#Start pubnub for accounts
for account in Account.get_all():
    if account.account_name == 'wink':
        wink.subscribe_devices(account)

app.run(host=host, debug=debug, port=port, threaded=threaded)
