""""
This server will run on the raspberry pi and will receive
commands from the andoid device
"""

from app_navigators.dropbox import DropboxNavigator
from app_navigators.base import BaseNavigator
from config import config
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common import exceptions as selenium_exceptions
from etc.response import Response
import copy
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
        try:
            if command[0] == "start":
                buttons_list = BROWSER.start()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=None)
            elif command[0] == "next":
                buttons_list = BROWSER.next()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=None)
            elif command[0] == "prev":
                buttons_list = BROWSER.prev()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=None)
            elif command[0] == "close":
                buttons_list = BROWSER.close()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=None)
            elif command[0] == "":
                buttons_list = BROWSER.home()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=None)
            elif self.path.startswith(BaseNavigator.connect_url):
                _, service_name = self.path.split(BaseNavigator.connect_url + "-")
                provider = BROWSER.get_provider(service_name)
                required = None
                buttons_list, fields_list = provider.is_redirect()
                provider.click_login_button_app()
                response = Response(code=200,
                                    current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=fields_list)
            elif command[0] == "connect-gdrive":
                BROWSER.click_login("Gdrive")
            # else:
            #     response = Response(code=405, message="Not allowed",
            #                         current_page=BROWSER.current_url,
            #                         buttons=None, fields=None)
            else:
                BROWSER.navigate_to(self.path)
                buttons_list, fields_list = BROWSER.get_current_page_options()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=fields_list)
        except IndexError:
            response = Response(code=405, message="Not allowed",
                                current_page=BROWSER.current_url,
                                buttons=None, fields=required)
        except:
            raise
        finally:
            self.send_response(response)

    def do_POST(self):
        buttons_list = None
        fields_list = None

        try:
            if not self.path_is_valid(self.path):
                buttons_list, fields_list = BROWSER.get_current_page_options()
                response = Response(code=404, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=fields_list, message="Not Found!")
            elif self.path.startswith(BaseNavigator.send_credentials):
                _, service_name = self.path.split(BaseNavigator.send_credentials + "-")
                provider = BROWSER.get_provider(service_name)
                data = self.rfile.read(int(self.headers['Content-Length']))
                data = json.loads(data)
                email = data[u'email']
                password = data[u'password']
                buttons_list = provider.do_login_service(email, password)
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=None)
            elif self.path.startswith(BaseNavigator.click_login):
                _, service_name = self.path.split(BaseNavigator.click_login + "-")
                provider = BROWSER.get_provider(service_name)
                buttons_list = provider.click_login_service()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=buttons_list, fields=None)
            elif self.path.startswith(BaseNavigator.accept_authorization_url):
                _, service_name = self.path.split(BaseNavigator.accept_authorization_url + "-")
                provider = BROWSER.get_provider(service_name)
                provider.accept_authorization()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=None, fields=None)
                self.send_response(response)
                # self.send_response(200)
            elif self.path.startswith(BaseNavigator.deny_authorization_url):
                _, service_name = self.path.split(BaseNavigator.deny_authorization + "-")
                provider = BROWSER.get_provider(service_name)
                provider.deny_authorization()
                response = Response(code=200, current_page=BROWSER.current_url,
                                    buttons=None, fields=None)
                self.send_response(response)
                # self.send_response(200)
        except selenium_exceptions.NoSuchElementException:
            response = Response(code=405, message="Not allowed",
                                current_page=BROWSER.current_url,
                                buttons=buttons_list, fields=fields_list)
        finally:
            self.send_response(response)

    def path_is_valid(self, path):
        base = BaseNavigator()
        for item in base.get_class_variables():
            try:
                resource, service = path.split(getattr(base, item) + '-')
            except ValueError:
                continue
            if resource != '':
                continue
            if service in BROWSER.providers_list.keys():
                return True
        return False

    def send_response(self, response):
        buttons_list = response.buttons
        fields_list = response.fields
        if buttons_list is None and fields_list is None:
            buttons_list, fields_list = BROWSER.get_current_page_options()
        elif buttons_list is None:
            buttons_list, _ = BROWSER.get_current_page_options()
        elif fields_list is None:
            _, fields_list = BROWSER.get_current_page_options()
        SimpleHTTPServer.SimpleHTTPRequestHandler.send_response(self, response.code, response.message)
        self.send_header("current_page", BROWSER.current_url.replace(APP_URL, ""))
        if buttons_list is not None:
            self.send_header("buttons", ','.join(buttons_list))
        else:
            self.send_header("buttons", '')
        if fields_list is not None:
            self.send_header("input_fields", ','.join(fields_list))
        else:
            self.send_header("input_fields", '')


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
    providers_list = {}
    gallery_options = ['start', 'next', 'prev', 'close']

    def __init__(self):
        WebDriver.__init__(self)
        self.maximize_window()
        self.providers_list[DropboxNavigator.name] = DropboxNavigator(browser=self)

    def start(self):
        element = self.find_elements_by_id("folder")
        element[0].click()
        return copy.deepcopy(self.gallery_options).remove('start')

    def next(self):
        element = self.find_elements_by_class_name("right")
        element[0].click()
        return copy.deepcopy(self.gallery_options).remove('next')

    def prev(self):
        element = self.find_elements_by_class_name("left")
        element[0].click()
        return copy.deepcopy(self.gallery_options).remove('prev')

    def close(self):
        element = self.find_elements_by_class_name("close")
        element[0].click()
        return copy.deepcopy(self.gallery_options).remove('close')

    def navigate_to(self, url):
        self.get(APP_URL[:-1] + url)
        print "get %s" % url

    def home(self):
        self.get(APP_URL)
        return self.get_home_buttons()

    def get_home_buttons(self):
        elements = self.find_elements_by_tag_name("input")
        return [item.get_attribute("value").encode('utf-8') for item in elements]

    def get_provider(self, name):
        return self.providers_list.get(name)

    def get_current_page_options(self):
        fields = None
        buttons = None
        path = self.current_url.replace(APP_URL, "")
        if path == '':
            buttons = self.get_home_buttons()
        elif path.startswith(BaseNavigator.connect_url):
            return
        elif path.startswith(BaseNavigator.send_credentials):
            return
        elif path.startswith(BaseNavigator.click_login):
            return
        elif path.startswith(BaseNavigator.accept_authorization_url):
            return
        elif path.startswith(BaseNavigator.deny_authorization_url):
            return
        elif path.startswith(DropboxNavigator.service_auth_url):
            provider = self.get_provider(DropboxNavigator.name)
            buttons, fields = provider.is_redirect()
        else:
            buttons = ["start", "next", "prev", "close"]
        return buttons, fields



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


