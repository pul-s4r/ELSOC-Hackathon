from flask import Flask

app = Flask(__name__)

node_list = {}
# Format:
# {roomname: [serial object, noise level, clients, active, process]}

client_list = {}
# Format:
# {clientname: [client #, room allocated]}
