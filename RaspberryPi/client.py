""""
Dummy client to simulate sending commands to raspberry pi server
"""

import requests
import socket
import httplib
from config import config
import time


class Client:
    def __init__(self, server, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))

    def send_stuff(self, to_send):
        self.socket.sendall(to_send)

def click_connect_dropbox():
    response = requests.get("http://localhost:9999/connect-dropbox")
    print response.headers, response.status_code
    time.sleep(3)
    try:
        l = response.headers.get('required')
        list = l.split(",")
        print [item for item in list]
    except:
        pass

def send_dropbox_credentials():
    data = {"email": "some@email.com", "password": "12345"}
    response = requests.post("http://localhost:9999/send-credentials-dropbox", json=data)
    print response.headers, response.status_code
    time.sleep(3)

def get_existing_folder():
    response = requests.get("http://localhost:9999/Dropbox/some/folder")
    print response.headers, response.status_code

def home():
    response = requests.get("http://localhost:9999/")
    print response.headers, response.status_code
    time.sleep(3)


def click_dropbox_login():
    response = requests.post("http://localhost:9999/click-login-dropbox")
    print response.headers, response.status_code
    time.sleep(3)

def allow_access():
    response = requests.post("http://localhost:9999/accept-authorization-dropbox")
    print response.headers, response.status_code
    time.sleep(3)

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args()

    CONF = config.compute_config(parsed_arguments.config, "android_server")

    # home()
    # click_connect_dropbox()
    # send_dropbox_credentials()
    # click_dropbox_login()
    # allow_access()
    get_existing_folder()


