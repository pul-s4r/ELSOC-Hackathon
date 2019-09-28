from flask import Flask, render_template, redirect, url_for, abort, session
import flask
import threading
import serial
from server import app, node_list, client_list
# from src import connect
# Need this workaround to avoid importing request from routes, which results
# in an unusable method attribute
request_real = flask.request;

def init_connection(port, baud):
    arduino = serial.Serial(port, baud, timeout=0.1)
    return arduino

def read_int(roomname):
    node = node_list[roomname]
    arduino = node[0]
    while True:
        data_raw = arduino.readline()[:-2]
        data_str = data_raw.decode("utf-8")

        try:
            data = int(data_str)
        except ValueError:
            data = None
        if data:
            # print(data)
            # set noise level
            node_list[roomname][1] = data
            # return data

    return None

def init_node_data():
    for key, value in node_list.items():
        #indicates that thread has already been activated
        if not node_list[key][3]:
            # print("Not active")
            node_thread = threading.Thread(name=key, target=read_int, args=(key,))
            node_thread.start()
            node_list[key][4] = node_thread
            node_list[key][3] = True

def select_room():
    noise_levels = {}
    occupancy = {}
    for key, value in node_list.items():
        noise_levels.update({key: value[1]})
        occupancy.update({key: len(value[2])})
    # print(noise_levels)
    # print(occupancy)

    min_noise = min(noise_levels, key=noise_levels.get)
    min_room = min(occupancy, key=occupancy.get)
    print("Min noise: " + str(min_noise))
    print("Min occupants: " + str(min_room))
    # if room numbers comparable, return least noisy
    if min_room == min_noise:
        return min_noise
    # if quietest room has only a few more people, return least noisy
    elif occupancy[min_noise] > occupancy[min_room] + 3:
        return min_noise
    # if quietest room is more crowded, return least crowded
    elif occupancy[min_noise] > occupancy[min_room]:
        return min_room
    # otherwise, fill up rooms evenly i.e. least crowded first
    else:
        return min_room

@app.route('/')
@app.route('/index')
def index():
    # print(node_list)
    nodes = node_list
    return render_template("index.html", nodes=nodes)

@app.route('/nodes')
def nodes():
    nodes = node_list
    return render_template("nodes.html", nodes=nodes)

@app.route('/nodes/add', methods=["GET", "POST"])
def nodes_add():
    if request_real.method == 'POST':
        form_values = dict(request_real.values)
        try:
            roomname = form_values['roomname']
            serial_address = form_values['serial_address']

            arduino = init_connection(serial_address, 115200)
            node_list.update({roomname: [arduino, 0, [], False, None]})
            init_node_data()
        except ValueError:
            pass
    return render_template("add_nodes.html", nodes=nodes)

@app.route('/nodes/delete')
def nodes_delete():
    return "Remove a node"

@app.route('/request')
def request():
    return "Log of all requests received"

@app.route('/request/make', methods=["GET", "POST"])
def request_make():
    if request_real.method == 'POST':
        form_values = dict(request_real.values)
        try:
            clientname = form_values['client_name']
            client_list.update({clientname: [hash(clientname), None]})
            room_to_assign = select_room()
            client_list[clientname][1] = room_to_assign
            node_list[room_to_assign][2].append(clientname)
        except ValueError:
            pass

    return render_template("add_client.html", nodes=nodes)

@app.route('/request/result')
def request_result():
    return "See confirmation (or rejection) of study spot"
