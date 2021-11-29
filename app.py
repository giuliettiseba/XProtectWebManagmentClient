from datetime import datetime, timedelta

import requests
from flask import Flask, render_template, request
import identity_provider
import json
from api_gateway import Gateway

app = Flask(__name__)

token_expires_at = datetime.now()
access_token = ''
session = ''
api_gateway = ''


def get_token_decorator(function):
    def wrapper():
        api_gateway, session, access_token = get_token()
        return function(api_gateway, session, access_token)

    wrapper.__name__ = function.__name__
    return wrapper


def get_server_info():
    username = 'milestone'
    password = 'Milestone1$'
    server_url = 'http://10.1.0.93'
    return username, password, server_url


def get_token():
    global token_expires_at, access_token, session, api_gateway
    print(f"token expires in: {(token_expires_at - datetime.now()).seconds}")
    time_to_live = token_expires_at - datetime.now()
    if time_to_live.days < 0 or time_to_live.seconds < 60:
        session = requests.Session()
        username, password, server_url = get_server_info()
        token_response = identity_provider.get_token(session, username, password, server_url)
        token_dict = json.loads(token_response)
        token_expires_at = datetime.now() + timedelta(seconds=token_dict['expires_in'])
        access_token = token_dict["access_token"]
        api_gateway = Gateway(server_url)
    return api_gateway, session, access_token


@app.route('/<type>/<item>')
def get_details_by_id(type, item):
    api_gateway, session, access_token = get_token()
    details = \
        json.loads(api_gateway.get_single(session, type, item, access_token))['data']
    return render_template('details.html', details=details)


@app.route('/cameras')
@get_token_decorator
def show_cameras(api_gateway, session, access_token):  # put application's code here
    cameras_json = api_gateway.get(session, "Cameras", access_token)
    cameras = json.loads(cameras_json)['array']
    return render_template('cameras.html', cameras=cameras)


@app.route('/recordingservers')
@get_token_decorator
def show_recording_servers(api_gateway, session, access_token):
    sites = json.loads(api_gateway.get(session, "sites", access_token))['array']
    site = sites[0]['relations']['self']['id']

    recording_servers = \
        json.loads(api_gateway.get_child_items(session, "sites", site, "recordingServers", access_token))['array']
    return render_template('recordingservers.html', array=recording_servers)


@app.route('/license/<item>')
def get_licence_details(item):
    api_gateway, session, access_token = get_token()
    details = \
        json.loads(api_gateway.get_child_items(session, "licenseInformations", item, "LicenseDetails", access_token))[
            'array']
    return render_template('license.html', details=details)


@app.route('/cameraGroups')
def camera_groups():
    tasks = ['AddCameraGroup']
    items_json = get_json_from_api_gateway("cameraGroups")
    return render_template('table.html', availableTask=tasks, kind='cameraGroups', cameras=items_json)


@app.route('/cameraGroups/AddCameraGroup', methods=['GET', 'POST', 'DELETE'])
def add_camera_group():
    api_gateway, session, access_token = get_token()
    data = request.form
    create_payload = json.dumps({
        "name": data.get("name"),
        "description": data.get("description"),
    })
    create_response = api_gateway.create_item(session, "cameraGroups", create_payload, access_token)
    print(create_response, end='\n\n')

    response = json.loads(create_response)

    if (response.get('result')):
        successMessage = {"state": response['result']['state'], 'errorCode': "200"}
        return successMessage
    else:
        errorCode = response['error']['httpCode']
        errorMessage = response['error']['details'][0]
        errorMessage['errorCode'] = errorCode
        return errorMessage


@app.route('/')
def get_full_tree():
    management_server_arr = []

    for recording_server in get_json_from_api_gateway('recordingServers'):
        hardwares = get_hardware(recording_server)
        recording_server_hardware_arr = []

        for hardware in hardwares:
            cameras = get_cameras(hardware)
            hardware_cameras_arr = []

            for camera in cameras:
                hardware_cameras_arr.append(create_node_entry(camera['displayName'], ['cameras', camera['id']], ''))
            recording_server_hardware_arr.append(
                create_node_entry(hardware['displayName'], ['hardware', hardware['id']], hardware_cameras_arr))
        management_server_arr.append(
            create_node_entry(recording_server['displayName'], ['recordingServers', recording_server['id']],
                              recording_server_hardware_arr))

    root_arr = [{'label': 'Recording Servers', 'value': ['RecordingServers', ''],
                 'children': management_server_arr}]

    licenseInformation_arr = []
    for _license in get_json_from_api_gateway('licenseInformations'):
        licenseInformation_arr.append(
            (create_node_entry(_license['displayName'], ['license', _license['relations']['self']['id']], '')))
    root_arr.append((create_node_entry('License', ['Licenses', ''], licenseInformation_arr)))

    groups_arr = []
    camera_group_arr = []
    for cameraGroup in get_json_from_api_gateway('cameraGroups'):
        camera_group_arr.append(create_node_entry(cameraGroup['displayName'], ['cameraGroups', cameraGroup['id']], ''))
    groups_arr.append(create_node_entry('Cameras', ['cameraGroups', ''], camera_group_arr))

    groups_arr.append(create_node_entry('Microphones', ['microphonesGroup', ''], ''))
    groups_arr.append(create_node_entry('Speakers', ['group_cameras', ''], ''))
    groups_arr.append(create_node_entry('Metadata', ['group_cameras', ''], ''))
    groups_arr.append(create_node_entry('Output', ['group_cameras', ''], ''))
    groups_arr.append(create_node_entry('Input', ['group_cameras', ''], ''))

    root_arr.append(create_node_entry('Groups', ['Groups', ''], groups_arr))

    root_arr.append(create_node_entry('Access Control', ['Access Control', ''], ''))
    root_arr.append(create_node_entry('Clients', ['Clients', ''], ''))
    root_arr.append(create_node_entry('Rules', ['Rules', ''], ''))
    root_arr.append(create_node_entry('Security', ['Security', ''], ''))
    root_arr.append(create_node_entry('Alarms', ['Alarms', ''], ''))

    return render_template('index.html', list_ms_rs=root_arr)


if __name__ == '__main__':
    app.run()


def create_node_entry(label, value, children):
    return {'label': label, 'value': value,
            'children': children}


def get_json_from_api_gateway(param):
    api_gateway, session, access_token = get_token()
    _json = api_gateway.get(session, param, access_token)
    return json.loads(_json)['array']


def get_hardware(recording_server):
    api_gateway, session, access_token = get_token()
    return json.loads(
        api_gateway.get_child_items(session, "recordingServers", recording_server["id"], "hardware", access_token))[
        'array']


def get_cameras(hardware):
    api_gateway, session, access_token = get_token()
    return json.loads(api_gateway.get_child_items(session, "hardware", hardware["id"], "cameras", access_token))[
        'array']
