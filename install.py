#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import subprocess
from getpass import getuser
import hub.auth

def systemd_setup(config):
    try:
        with open("/dev/null","w") as out:
            subprocess.call(['systemctl'],stdout=out)
    except OSError:
        return False
    new = []
    cwd = os.getcwd()
    command = "/usr/bin/python2 " + cwd + "/runserver.py -c " + config
    with open(support_dir + "systemd.unit", "r") as f:
        for line in f:
            line = line.replace("<DIRECTORY>",cwd)
            line = line.replace("<COMMAND>", command)
            new.append(line)
    with open("/lib/systemd/system/iot-hub.service", "w+") as f:
        f.writelines(new)
    print("Finished installing webserver, now conifiguring hostapd and dnsmasq")
    new = []
    with open(support_dir + "hostapd.conf", "r") as f:
        for line in f:
            line = line.replace("<SSID>", ssid)
            line = line.replace("<INTERFACE>", interface)
            line = line.replace("<PASSWORD>", password)
            new.append(line)
    with open("/etc/hostapd/hostapd.conf", "w+") as f:
        f.writelines(new)
    new = []
    sub_ip = ip.rsplit(".", 1)[0]
    with open(support_dir + "dnsmasq.conf", "r") as f:
        for line in f:
            line = line.replace("<INTERFACE>",interface)
            line = line.replace("<SUB_IP>", sub_ip)
            new.append(line)
    with open("/etc/dnsmasq.conf", "w+") as f:
        f.writelines(new)
    with open("/dev/null","w") as out:
        subprocess.call(['systemctl','daemon-reload'],stdout=out)
        subprocess.call(['systemctl','enable','iot-hub.service'],stdout=out)
        subprocess.call(['systemctl','enable','dnsmasq.service'],stdout=out)
        subprocess.call(['systemctl','enable','hostapd.service'],stdout=out)
    new = []
    with open(support_dir + "interfaces") as f:
        for line in f:
            line = line.replace("<IP>", ip)
            new.append(line)
    try:
        with open("/etc/network/interfaces", "a") as f:
            f.writelines(new)
    except IOError:
        print("Was unable to set the IP of " + interface + ".")
        print("Please set the IP manually using these settings:")
        for line in new:
            print(line)
    return True

def initd_setup(config):
    script_path = "/etc/init.d/iot-hub"
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
        subprocess.call(["update-rc.d","-hub","defaults"])
    return True

if __name__ == "__main__":
    if getuser() != 'root':
        print("Must be run as root...")
        exit(1)

    support_dir = "support_files/"
    dconfig    = "arguments.config"
    durl       = "https://home.nolanfoster.me/v1"
    dport      = "5000"
    dhost      = "0.0.0.0"
    dthreaded  = "true"
    dinterface = "wlan0"
    dip        = "192.168.0.1"
    dssid      = "IOT-HUB"
    config     = raw_input("Config File["+dconfig+"]:")
    url        = raw_input("WebAPI URL["+durl+"]:")
    apikey     = token_hex([nbytes=16])
    ssid       = raw_input("Access Point SSID["+dssid+"]:")
    password   = raw_input("Access Point Password[REQUIRED]:")
    interface  = raw_input("Interface["+dinterface+"]:")
    ip         = raw_input("Interface IP["+dip+"]:")
    port       = raw_input("Port ["+dport+"]:")
    host       = raw_input("Host ["+dhost+"]:")
    if apikey == "":
        print("No API key was generated...Exiting")
        exit(1)
    if config == "":
        config = dconfig
    if url == "":
        url = durl
    if port == "":
        port = dport
    if host == "":
        host = dhost
    if interface == "":
        interface = dinterface
    if ip == "":
        ip = dip
    if ssid == "":
        ssid = dssid

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
    else:
        print("Installation on non-systemd linux is not supported...Exiting")
        exit(1)
    #elif initd_setup(config):
    #    print("Finished initd setup")
    #    run = raw_input("All set, run now and test? [y/n]:")
    #    if run.lower() in ["y", "yes"]:
    #        subprocess.call(['service','stratusprint-hub','start'])
