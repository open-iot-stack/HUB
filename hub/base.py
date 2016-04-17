#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hub
from flask import url_for
from flask import json
from flask import render_template
from flask import abort
from flask import request
from jobs import Jobs
from hub import app
from hub.database import db_session

from models import Printer
from models import Job
from models import File

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove

@app.route('/list', methods=['GET'])
def list_peripherals():
    """Returns a json list of the peripherals curerntly registered"""

    return json.jsonify(hub.conf.read_data())

@app.route('/register', methods=['GET', 'POST'])
def register_peripheral():
    """Webpage to register the type of a given sensor
    This should be done before activating the sensor.
    :returns: webpage of result
    """

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        uuid = int(request.form.get('uuid'))
        pertype = request.form.get('pertype')
        if request.form.get('is_update'):
            success = hub.conf.update_data({uuid: pertype})
        else:
            success = hub.conf.add_data({uuid: pertype})

        if success:
            return json.jsonify(
                    {
                        "message": str(uuid)
                        + " has been registered as " + pertype
                    })
        else:
            return json.jsonify(
                    {
                        "message": str(uuid)
                        + " was not registered, are you updating?"
                    })
    abort(405)

@app.route('/')
def index():
    p = {
        "uuid": 1234,
        "jobs": Jobs()
    }
    p["jobs"].add("test2")
    p["jobs"].add("test1")
    hub.printers_wrapper.add(p)
    p = hub.printers_wrapper.get(1234)
    return json.jsonify(p)
    exit()
    fdate = str(dt.utcnow().isoformat()[:-3])+'Z'
    j = Job(uuid=3121, created_at=fdate, updated_at=fdate,status="ERROR")
    j.file += [File(name="Holder.st",origin="remote",size=9123)]
    p.cjob = []
    p.jobs += [j]
    j2 = Job(uuid=3221,created_at=fdate,updated_at=fdate,status="ERROR")
    p.jobs+=[j2]
    db_session.add(p)
    db_session.commit()
    db_session.remove()
    #print Printer.query.all()
    return str(p)
    #print j
    uuid=0
    return "0 represents the UUID" + '<br>'\
         + url_for('register_peripheral') + '<br>'\
         + url_for('activate_sensor') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='start') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='cancel') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='pause') + '<br>'\
         + url_for('print_action' ,uuid=uuid, action='status') + '<br>'\
         + url_for('sensor_data'  ,uuid=uuid) + '<br>'
#    send_email(json.dumps(json_data,
#                          sort_keys = True,
#                          indent = 2,
#                          separators=(',', ':')
#                         ),
#              "Sensor Data",
#              snd_psswd = SND_PASSWD
#              )
