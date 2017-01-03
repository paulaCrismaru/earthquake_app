""""
This server will run on the raspberry pi and will receive
commands from the andoid device
"""

from config import config
from selenium.webdriver.firefox.webdriver import WebDriver

import json
import requests
import SocketServer
import sys
import SimpleHTTPServer
import threading
import time


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        """Serve a GET request."""
        command = self.path.split('/')
        command.remove('')
        if command[0] == "start":
            options = BROWSER.start()
        elif command[0] == "next":
            BROWSER.next()
            self.send_response(200)
        elif command[0] == "prev":
            BROWSER.prev()
            self.send_response(200)
        elif command[0] == "close":
            BROWSER.close()
            self.send_response(200)
        elif command[0] == '':
            options = BROWSER.home()
            self.send_response(200, buttons=options)
        elif command[0] == "connect-dropbox":
            BROWSER.click_login("Dropbox")
            if BROWSER.is_redirect_dropbox():
                self.send_response(200, required=['email', 'password'])
            else:
                self.send_response(200)
        elif command[0] == "connect-gdrive":
            BROWSER.click_login("Gdrive")

    def do_HEAD(self):
        """Serve a HEAD request."""
        self.send_head(200)

    def send_response(self, code, message=None, **new_fields):
        SimpleHTTPServer.SimpleHTTPRequestHandler.send_response(self, code, message)
        for field in new_fields:
            self.send_header(field, str(new_fields.get(field)))

    def do_POST(self):
        print "in post"
        data = self.rfile.read(int(self.headers['Content-Length']))
        print json.load(data)
        self.send_response(200)


class Server(SocketServer.TCPServer):
    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self, host, port):
        self.url = "http://%s:%s" % (host, port)
        self.log_message("Server started at %s" % (self.url))
        SocketServer.TCPServer.__init__(self, (host, port), Handler)

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" %
                         (self.log_date_time_string(),
                          format % args))

    def log_date_time_string(self):
        """Return the current time formatted for logging."""
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
            day, self.monthname[month], year, hh, mm, ss)
        return s


class FireFox(WebDriver):
    def __init__(self):
        WebDriver.__init__(self)
        self.maximize_window()

    def start(self):
        element = self.find_elements_by_id("folder")
        element[0].click()
        print "start"

    def next(self):
        element = self.find_elements_by_class_name("right")
        element[0].click()
        print "next"

    def prev(self):
        element = self.find_elements_by_class_name("left")
        element[0].click()
        print "prev"

    def close(self):
        element = self.find_elements_by_class_name("close")
        element[0].click()
        print "close"

    def navigate_to(self, url):
        self.get(url)
        print "get %s" % url

    def home(self):
        self.get(APP_URL)
        elements = self.find_elements_by_tag_name("input")
        return [item.get_attribute("value").encode('utf-8') for item in elements]

    def click_login(self, button):
        element = None
        if button == "Gdrive":
            element = self.find_elements_by_id("Gdrive-button")
        elif button == "Dropbox":
            element = self.find_elements_by_id("Dropbox-button")

        element[0].click()

    def is_redirect_dropbox(self):
        return self.current_url.encode('utf-8').startswith("https://www.dropbox.com/1/oauth2/authorize?")





BROWSER = None
APP_URL = None
if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args(sys.argv[1:])

    APP_CONF = config.compute_config(parsed_arguments.config, "app_server")
    APP_PROTOCOL, APP_HOST, APP_PORT = APP_CONF.protocol, APP_CONF.host, APP_CONF.port
    APP_URL = APP_CONF.protocol + "://" + APP_HOST + ":" + APP_PORT + "/"

    ANDROID_CONF = config.compute_config(parsed_arguments.config, "android_server")
    ANDROID_HOST, ANDROID_PORT = ANDROID_CONF.host, ANDROID_CONF.port
    BROWSER = FireFox()
    server = Server(ANDROID_HOST, int(ANDROID_PORT))
    server.serve_forever()


