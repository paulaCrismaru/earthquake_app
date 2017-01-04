""""
Dummy client to simulate sending commands to raspberry pi server
"""
import requests
import socket
import time
from config import config


class Client:
    def __init__(self, server, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))

    def send_stuff(self, to_send):
        self.socket.sendall(to_send)

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args()

    CONF = config.compute_config(parsed_arguments.config, "android_server")
    response = requests.get("http://localhost:1123")
    print response.headers
    time.sleep(3)

    response = requests.get("http://localhost:1123/connect-dropbox")
    print response.headers
    time.sleep(3)

    data = {"email": "whatever@whatever", "password": "1234"}
    response = requests.post("http://localhost:1123/send-data", json=data)
    print response.headers
    time.sleep(3)

