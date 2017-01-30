from flask import Flask, render_template, request, session, json, redirect, url_for
from urllib2 import Request, urlopen
from json import dumps

app = Flask(__name__)

@app.route("/wink/login", methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']
    values = dumps({
        "client_id": "quirky_wink_android_app",
        "client_secret": "e749124ad386a5a35c0ab554a4f2c045",
        "username": username,
        "password": password,
        "grant_type": "password",
    })

    headers = {"Content-Type": "application/json", "Connection": "keep-alive",
        "X-API-VERSION": "1.0 User-Agent: Wink/1.1.9 (iPhone; iOS 7.0.4; Scale/2.00)"}
    req = Request("https://winkapi.quirky.com/oauth2/token", data=values, headers=headers)
    response_body = urlopen(req).read()

    data = json.loads(response_body)

    access_token = data['data']['access_token']
    refresh_token = data['data']['refresh_token']

    session["access_token"] = access_token
    session["refresh_token"] = refresh_token

    print response_body

    return redirect(url_for('dashboard'))


def update_device_state(device_type, device_id):
    device_type = device_type
    device_id = device_id
    token = session["access_token"]
    headers = {"Authorization": "Bearer " + token}
    request = Request("https://winkapi.quirky.com/users/me/wink_devices/"+device_type+"/"+device_id, headers=headers)
    response_body = urlopen(request).read()
    data = json.loads(response_body)
    print response_body
    return dict(data)


def get_token_from_session():
    return session["access_token"]


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
