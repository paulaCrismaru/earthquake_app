""""
This server will run on the raspberry pi and will receive
commands from the andoid device
"""

from config import config
from selenium.webdriver.firefox.webdriver import WebDriver

import SocketServer
import sys


class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        print data
        if data == "start":
            element = DRIVER.find_elements_by_id("folder")
            element[0].click()
        elif data == "next":
            element = DRIVER.find_elements_by_class_name("right")
            element[0].click()
        elif data == "prev":
            element = DRIVER.find_elements_by_class_name("left")
            element[0].click()
        elif data == "close":
            element = DRIVER.find_elements_by_class_name("close")
            element[0].click()
        else:
            DRIVER.get(APP_URL + data)

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args(sys.argv[1:])

    APP_CONF = config.compute_config(parsed_arguments.config, "app_server")
    APP_PROTOCOL, APP_HOST, APP_PORT = APP_CONF.protocol, APP_CONF.host, APP_CONF.port
    APP_URL = APP_CONF.protocol + "://" + APP_HOST + ":" + APP_PORT + "/"

    ANDROID_CONF = config.compute_config(parsed_arguments.config, "android_server")
    ANDROID_HOST, ANDROID_PORT = ANDROID_CONF.host, ANDROID_CONF.port

    DRIVER = WebDriver()
    server = SocketServer.TCPServer((ANDROID_HOST, int(ANDROID_PORT)), Handler)

    DRIVER.maximize_window()
    DRIVER.get(APP_URL)
    server.serve_forever()


