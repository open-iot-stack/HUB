#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import subprocess
from getpass import getuser

def systemd_setup(config):
    try:
        with open("/dev/null","w") as out:
            subprocess.call(['systemctl'],stdout=out)
    except OSError:
        return False
    new = []
    cwd = os.getcwd()
    command = "/usr/bin/python2 " + cwd + "/runserver.py -c " + config
    with open("systemd.unit", "r") as f:
        for line in f:
            line = line.replace("<DIRECTORY>",cwd)
            line = line.replace("<COMMAND>", command)
            new.append(line)
    with open("/lib/systemd/system/stratusprint-hub.service", "w+") as f:
        f.writelines(new)
    with open("/dev/null","w") as out:
        subprocess.call(['systemctl','daemon-reload'],stdout=out)
        subprocess.call(['systemctl','enable','stratusprint-hub.service'],stdout=out)
    return True

def initd_setup(config):
    script_path = "/etc/init.d/stratusprint-hub"
    new = []
    cwd = os.getcwd()
    command = "/usr/bin/python2 " + cwd + "/runserver.py -c " + config
    with open("init.d.script", "r") as f:
        for line in f:
            line = line.replace("<DIRECTORY>",cwd)
            line = line.replace("<COMMAND>", command)
            new.append(line)
    with open(script_path, "w+") as f:
        f.writelines(new)
    os.chmod(script_path, 0755)
    with open("/dev/null","w") as out:
        subprocess.call(["update-rc.d","stratusprint-hub","defaults"])
    return True

if __name__ == "__main__":
    if getuser() != 'root':
        print("Must be run as root...")
        exit(1)

    dconfig = "arguments.config"
    durl = "https://dev.api.stratusprint.com/v1"
    dport = "5000"
    dhost = "0.0.0.0"
    dthreaded = "true"
    config = raw_input("Config File["+dconfig+"]:")
    url = raw_input("WebAPI URL["+durl+"]:")
    apikey     = raw_input("WebAPI Key[REQUIRED]:")
    port       = raw_input("Port ["+dport+"]:")
    host       = raw_input("Host ["+dhost+"]:")
    if apikey == "":
        print("No API key was entered...Exiting")
        exit(1)
    if config == "":
        config = dconfig
    if url == "":
        url = durl
    if port == "":
        port = dport
    if host == "":
        host = dhost

    with open(config, "w+") as f:
        f.writelines(["-w "     + str(url)    + "\n",
                      "-a "     + str(apikey) + "\n",
                      "-p "     + str(port)   + "\n",
                      "--host " + str(host)   + "\n",
                      "-t"                    + "\n"])
    if systemd_setup(config):
        print("Finished systemd setup")
        run = raw_input("All set, run now and test? [y/n]:")
        if run.lower() in ["y", "yes"]:
            subprocess.call(['systemctl','start','stratusprint-hub'])
    elif initd_setup(config):
        print("Finished initd setup")
        run = raw_input("All set, run now and test? [y/n]:")
        if run.lower() in ["y", "yes"]:
            subprocess.call(['service','stratusprint-hub','start'])
