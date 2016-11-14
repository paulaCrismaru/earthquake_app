""""
Dummy client to simulate sending commands to raspberry pi server
"""

import socket

from config import config


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER, PORT))

    def send_stuff(self, to_send):
        self.socket.sendall(to_send)

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args()

    CONF = config.compute_config(parsed_arguments.config, "android_server")

    SERVER = CONF.host
    PORT = int(CONF.port)

    c = Client()
    stuff = "start"
    # stuff = "next"
    # stuff = "close"
    c.send_stuff(stuff)
    c.socket.close()
