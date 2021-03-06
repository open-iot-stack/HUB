#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os, subprocess, stat
import random
from getpass import getuser
from base64 import b64encode

def systemd_setup(config, port):
    try:
        with open("/dev/null","w") as out:
            subprocess.call(['systemctl'],stdout=out)
    except OSError:
        return False
    new = []
    cwd = os.getcwd()
    command = "/usr/bin/python3 " + cwd + "/runserver.py -c " + config
    with open(support_dir + "systemd.unit", "r") as f:
        for line in f:
            line = line.replace("<DIRECTORY>",cwd)
            line = line.replace("<COMMAND>", command)
            new.append(line)
    with open("/lib/systemd/system/iot-hub.service", "w+") as f:
        f.writelines(new)
    print("Finished installing iot-hub service")
    new = []
    with open(support_dir + "systemd-ngrok.unit", "r") as f:
        for line in f:
            new.append(line)
    with open("/lib/systemd/system/ngrok-iot.service", "w+") as f:
        f.writelines(new)

    new = []
    with open(support_dir + "ngrok.conf", "r") as f:
        for line in f:
            line = line.replace("<PORT>",port)
            new.append(line)
    with open("/opt/ngrok/ngrok.yml", "w+") as f:
        f.writelines(new)
    print("Finished installing ngrok service")
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
        subprocess.call(['systemctl','enable','ngrok-iot.service'],stdout=out)
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
    os.chmod(script_path, stat.S_IRRWXU)
    with open("/dev/null","w") as out:
        subprocess.call(["update-rc.d","iot-hub","defaults"])
    return True

if __name__ == "__main__":
    if getuser() != 'root':
        print("Must be run as root...")
        exit(1)

    support_dir = "support_files/"
    dconfig    = "arguments.config"
    durl       = "https://home.nolanfoster.me/v1"
    dport      = str(random.randint(1000, 65535))
    dhost      = "0.0.0.0"
    dthreaded  = "true"
    dinterface = "wlan0"
    dip        = "192.168.42.1"
    dssid      = "IOT-HUB"
    config     = input("Config File["+dconfig+"]:")
    url        = input("WebAPI URL["+durl+"]:")
    apikey     = b64encode(os.urandom(32)).decode('utf-8')
    ssid       = input("Access Point SSID["+dssid+"]:")
    password   = input("Access Point Password[REQUIRED]:")
    interface  = input("Interface["+dinterface+"]:")
    ip         = input("Interface IP["+dip+"]:")
    port       = input("Port ["+dport+"]:")
    host       = input("Host ["+dhost+"]:")
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
    if systemd_setup(config, str(port)):
        print("Finished systemd setup")
        run = input("All set, run now and test? [y/n]:")
        if run.lower() in ["y", "yes"]:
            subprocess.call(['systemctl','start','iot-hub'])
    else:
        print("Installation on non-systemd linux is not supported...Exiting")
        exit(1)
    # elif initd_setup(config):
    #    print("Finished initd setup")
    #    run = raw_input("All set, run now and test? [y/n]:")
    #    if run.lower() in ["y", "yes"]:
    #        subprocess.call(['service','stratusprint-hub','start'])
