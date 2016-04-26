#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hub
from flask import url_for, json, render_template, abort, request
from hub import app
from hub.database import db_session
from flask_swagger import swagger

from models import Printer
from models import Job
from models import File

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove


@app.route("/swagger")
def spec():
    return json.jsonify(swagger(app))


@app.route("/docs")
def docs():
    return render_template('index.html')

@app.route('/list', methods=['GET'])
def list_peripherals():
    """
        List Peripherals
		Get list of peripherals currently registered
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns peripherals currently registered
        """
	
    return json.jsonify(hub.conf.read_data())

@app.route('/register', methods=['GET', 'POST'])
def register_peripheral():
    """Webpage to register the type of a given node
    This should be done before activating the node.
    :returns: webpage of result
    """
	"""
        Register Peripheral
		Registers node
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns "(action) successfully sent to the printer."
        """

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        id = int(request.form.get('id'))
        pertype = request.form.get('pertype')
        if request.form.get('is_update'):
            success = hub.conf.update_data({id: pertype})
        else:
            success = hub.conf.add_data({id: pertype})

        if success:
            return json.jsonify(
                    {
                        "message": str(id)
                        + " has been registered as " + pertype
                    })
        else:
            return json.jsonify(
                    {
                        "message": str(id)
                        + " was not registered, are you updating?"
                    })
    abort(405)

@app.route('/')
def index():
    id=0

    return "0 represents the UUID" + '<br>'\
         + url_for('register_peripheral') + '<br>'\
         + url_for('activate_node') + '<br>'\
         + url_for('print_action' ,id=id, action='start') + '<br>'\
         + url_for('print_action' ,id=id, action='cancel') + '<br>'\
         + url_for('print_action' ,id=id, action='pause') + '<br>'\
         + url_for('print_status' ,id=id) + '<br>'\
         + url_for('node_data'  ,id=id) + '<br>'
