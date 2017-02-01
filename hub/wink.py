from pubnub import Pubnub
from flask import Flask, render_template, request, session, json, redirect, url_for
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from json import dumps
import hub
from .chest import Chest
from hub import app
from hub.logger import Log
from .database import db_session
from hub.models import Account, Node, Sensor
import sys

global log

log = Log()

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
    }).encode('utf-8')

    headers = {"Content-Type": "application/json", "Connection": "keep-alive",
        "X-API-VERSION": "1.0 User-Agent: Wink/1.1.9 (iPhone; iOS 7.0.4; Scale/2.00)"}

    req = Request("https://winkapi.quirky.com/oauth2/token", data=values, headers=headers)
    response_body = urlopen(req).read()

    data = json.loads(response_body)

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    token_endpoint = data['token_endpoint']
    if access_token and refresh_token and token_endpoint:
        account = Account.get_by_name('wink')
        if account:
            account.update(web_token = access_token, web_refresh_token = refresh_token)
        else:
            account = Account('wink',access_token, refresh_token, token_endpoint)

        devices = get_all_devices(account)
        channels = []
        sub_key = ''


        node_id = ''
        node_frienly_id = ''
        for device in devices['data']:
             if 'hub_id' in device:
                 node_id = device['hub_id']
                 node_frienly_id = device['name']
                 break
        if node_id:
            node = Node.get_by_id(node_id)
            if node is None:
                node = Node(node_id, '0', node_frienly_id)
        #register node
        for device in devices['data']:
            sub = device['subscription']
            if sub:
                channels.append(sub['pubnub']['channel'])
                sub_key = sub['pubnub']['subscribe_key']
            sensor = Sensor.get_by_webid(device['uuid'])
            if sensor is None:
                Sensor(node.id, 'wink',
                webid=device['uuid'],
                value=json.dumps(device['desired_state']),
                raw=json.dumps(device),
                friendly_id=json.dumps(device['name']).replace('"',''),
                state= "CONNECTED" if json.dumps(device['last_reading']['connection']) == 'true'else "DISCONNECTED")
            else:
                sensor.webid = device['uuid']
                sensor.value = json.dumps(device['desired_state'])
                sensor.raw = json.dumps(device)
                sensor.friendly_id = json.dumps(device['name']).replace('"','')
                sensor.state = "CONNECTED" if json.dumps(device['last_reading']['connection']) == 'true'else "DISCONNECTED"
                sensor.update()

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
            "refresh_token": account.web_refresh_token,
        }).encode('utf-8')

        headers = {"Content-Type": "application/json", "Connection": "keep-alive",
            "X-API-VERSION": "1.0 User-Agent: Wink/1.1.9 (iPhone; iOS 7.0.4; Scale/2.00)"}
        req = Request("https://winkapi.quirky.com/oauth2/token", data=values, headers=headers)
        response_body = urlopen(req).read()

        data = json.loads(response_body)

        access_token = data['access_token']
        refresh_token = data['refresh_token']
        token_endpoint = data['token_endpoint']
        if access_token and refresh_token and token_endpoint:
            account = Account.get_by_name('wink')
            if account:
                account.update(web_token = access_token, web_refresh_token = refresh_token)
            else:
                account = Account('wink',access_token, refresh_token, token_endpoint)
            return account
        else:
            abort(404)

def subscribe_devices(account):
    devices = get_all_devices(account)
    channels = []
    sub_key = ''

    for device in devices['data']:
        sub = device['subscription']
        if sub:
            channels.append(sub['pubnub']['channel'])
            sub_key = sub['pubnub']['subscribe_key']

    subcribe_devices_to_pub_nub(sub_key, channels)

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
    return dict(data)


def get_token_from_session():
    return session["access_token"]

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

def subcribe_devices_to_pub_nub(sub_key, channels):
    global log
    pubnub = Pubnub(publish_key="", subscribe_key=sub_key,ssl_on=True)
    def callback(message, channel):
        response = json.loads(message)
        sensor = Sensor.get_by_webid(response['uuid'])
        sensor.webid = response['uuid']
        sensor.value = json.dumps(response['desired_state'])
        sensor.raw = json.dumps(response)
        sensor.friendly_id = json.dumps(response['name']).replace('"','')
        sensor.state = "CONNECTED" if json.dumps(response['last_reading']['connection']) == 'true'else "DISCONNECTED"
        sensor.update()

    def error(message):
        log.log("Pubnub Error: "+message)

    def connect(message):
        log.log("Pubnub Connected: "+message)

    def reconnect(message):
        log.log("Pubnub Reconnected: "+message)


    def disconnect(message):
        log.log("Pubnub Disconnected: "+message)

    for channel in channels:
        pubnub.subscribe(channels=channel, callback=callback, error=callback,
                         connect=connect, reconnect=reconnect, disconnect=disconnect)
