import hub
from flask import request, jsonify
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            valid = verify_auth_token(request)
        except Exception as e:
            response = jsonify(message='Invalid authorization header')
            response.status_code = 401
            return response

        if not valid:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response

        return f(*args, **kwargs)

    return decorated_function

def verify_auth_token(req):
    token = req.headers.get('Authorization').split()
    if token[0] != 'Bearer':
        raise Exception
    return token[1] == hub.WEB_API_KEY