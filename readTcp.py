#!/usr/bin/python3

import socket

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 65432

client = socket.socket()
host = DEFAULT_HOST
port = DEFAULT_PORT
client.connect((host, port))

while True:
    try:
        msg = client.recv(1024).decode('ascii').strip()
        print(msg)
    except socket.error:
        socket.close()
        break

