#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hub
from flask import url_for, json, render_template, abort, request
from hub import app
from hub.database import db_session
from flask_swagger import swagger

from .models import Printer
from .models import Job
from .models import File

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

@app.route('/register', methods=['GET'])
def get_register_peripheral():
    """
        Get Register Peripheral
        Get node registration information
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns webpage of result
        """

    if request.method == "GET":
        return render_template("register.html")
    abort(405)

@app.route('/register', methods=['POST'])
def register_peripheral():
    """
        Register Peripheral
        Registers node type. Should be done before activating node.
        ---
        tags:
          - sensors
        responses:
          200:
            description: Returns "(id) has been registered as (type)"
        """

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
    return 0
