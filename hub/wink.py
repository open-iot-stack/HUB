from pubnub import Pubnub
from flask import Flask, render_template, request, session, json, redirect, url_for
from urllib2 import Request, urlopen
from json import dumps
import hub
from chest import Chest
from hub import app
from database import db_session
from hub.models import Account, Node, Sensor
import sys

@app.route("/wink", methods=['POST'])
def test():
    return "{'Hello!'}"


@app.route("/wink/login", methods=['POST'])
def login():

    username = request.json.get('username')
    password = request.json.get('password')
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
    print sys.stderr, data

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    token_endpoint = data['token_endpoint']
    if access_token and refresh_token and token_endpoint:
        account = Account.get_by_name('wink')
        if account:
            account.update(web_token = access_token, web_refresh_token = refresh_token)
            print sys.stderr, "UPDATE_ACCOUNT"
        else:
            account = Account('wink',access_token, refresh_token, token_endpoint)
            print sys.stderr, "NEW ACCOUNT"

        devices = get_all_devices(account)
        channels = []
        sub_key = ''

        node_id = ''
        for device in devices['data']:
             if 'hub_id' in device:
                 node_id = device['hub_id']
        print(node_id)
        if node_id:
            node = Node.get_by_id(node_id)
            if node is None:
                node = Node(node_id, '0')
        #register node
        for device in devices['data']:
            sub = device['subscription']
            if sub:
                channels.append(sub['pubnub']['channel'])
                sub_key = sub['pubnub']['subscribe_key']
                sensor = Sensor.get_by_webid(device['uuid'])
                if sensor is None:
                    Sensor(node.id, 0, 'wink', device['uuid'])

        subcribe_devices_to_pub_nub(sub_key, channels)
        return "success"
    else:
        abort(404)

def refresh_token():
    account = Account.get_by_name('wink')

    if account:
        values = dumps({
            "client_id": "quirky_wink_android_app",
            "client_secret": "e749124ad386a5a35c0ab554a4f2c045",
            "grant_type": "refresh_token",
            "refresh_token": account.refresh_token,
        })

        headers = {"Content-Type": "application/json", "Connection": "keep-alive",
            "X-API-VERSION": "1.0 User-Agent: Wink/1.1.9 (iPhone; iOS 7.0.4; Scale/2.00)"}
        req = Request("https://winkapi.quirky.com/oauth2/token", data=values, headers=headers)
        response_body = urlopen(req).read()

        data = json.loads(response_body)
        print sys.stderr, data

        access_token = data['access_token']
        refresh_token = data['refresh_token']
        token_endpoint = data['token_endpoint']
        if access_token and refresh_token and token_endpoint:
            account = Account.get_by_name('wink')
            if account:
                account.update(web_token = access_token, web_refresh_token = refresh_token)
                print sys.stderr, "UPDATE_ACCOUNT"
            else:
                account = Account('wink',access_token, refresh_token, token_endpoint)
                print sys.stderr, "NEW ACCOUNT"

            print sys.stderr, account
            return "success"
        else:
            abort(404)

def get_all_devices(account):
    headers = {"Authorization": "Bearer " + account.web_token}
    req = Request("https://winkapi.quirky.com/users/me/wink_devices", headers=headers)
    response_body = urlopen(req).read()
    data = json.loads(response_body)
    return data

def update_device_state(device_json):
    device_type = 'light_bulbs'
    device_id = device_json['light_bulb_id']
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

def subcribe_devices_to_pub_nub(sub_key, channels):

    pubnub = Pubnub(publish_key="", subscribe_key=sub_key,ssl_on=True)
    def callback(message, channel):
        print(message)

    def error(message):
        print("ERROR : " + str(message))

    def connect(message):
        print("CONNECTED")

    def reconnect(message):
        print("RECONNECTED")


    def disconnect(message):
        print("DISCONNECTED")


    for channel in channels:
        pubnub.subscribe(channels=channel, callback=callback, error=callback,
                         connect=connect, reconnect=reconnect, disconnect=disconnect)
