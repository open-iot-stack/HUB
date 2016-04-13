#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hub
from flask import url_for
from flask import json
from flask import render_template
from flask import abort
from flask import request
from hub import app

@app.route('/register', methods=['GET', 'POST'])
def register_peripheral():
    """Webpage to register the type of a given sensor
    This should be done before activating the sensor.
    :returns: webpage of result
    """

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        uuid = request.form.get('uuid')
        pertype = request.form.get('pertype')
        if request.form.get('is_update'):
            success = hub.conf.update_data({uuid: pertype})
        else:
            success = hub.conf.add_data({uuid: pertype})

        if success:
            return json.jsonify(
                    {
                        "message": uuid + " has been registered as " + pertype
                    })
        else:
            return json.jsonify(
                    {
                        "message": uuid + " was not registered, are you updating?"
                    })

    abort(405)

@app.route('/')
def index():
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
