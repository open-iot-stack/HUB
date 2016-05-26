#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os

def authenticate(request):
    """Will make sure the connecting client is allowed
    to access the webserver. Authentication is based on
    header api-key or ip address on the local network

    :request: TODO
    :returns: TODO

    """
    ip     = request.remote_addr
    triple = ip.rsplit(".", 1)[0]
    if triple == "192.168.0":
        return True
    headers = request.headers
    api_key = headers.get("Authorization")
    if api_key == webapi_key:
        return True
    return False

def generate():
    """Returns a randomly generated api_key
    :returns: TODO

    """
    return os.urandom(32).encode("hex")
