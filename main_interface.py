#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from config import config
from flask import Flask, session, redirect, url_for, \
    request, render_template, jsonify, send_from_directory
from lib.CloudStorage.Dropbox import Dropbox
from dropbox import DropboxOAuth2Flow, oauth
import hashlib
import os
import Redis
import threading
import urllib
import httplib2
import json
from apiclient import discovery
from oauth2client import client

app = Flask(__name__)

CONNECTED = None
DBX = None
TREE = None
DB = None
REFRESH_DONE = None


@app.route('/')
def home():
    return render_template('connect.html', dict=TREE,
                           folder_name='home',
                           services_list=TREE.keys()
                           )


@app.route('/<path:path>')
def main(path, image_link=None):
    if CONNECTED:
        image_link_list = []
        for service in cloud_services:
            folder_name = path
            folder_name = [unicode.encode(item, 'utf-8') for item in folder_name.split('/')]
            folder_name.remove(service.name)
            folder_name = '/'.join(folder_name)
            link_list = get_cached(folder_name)
            # if not REFRESH_DONE or link_list is None:
            image_link_list = DBX.get_files_folder_temp_link_list("/" + folder_name)
            # cache(path, link_list)
            # else:
            #     print "from cache"
            # image_link_list = image_link_list + link_list
        return render_template(CONF.index, dict=TREE,
                               folder_name=folder_name,
                               image_link=image_link,
                               image_link_list=image_link_list)
    else:
        return redirect(url_for('connect'))

#
# @app.route('/<path:path>')
# def main(path, image_link=None):
#     if 'credentials' not in session:
#         return redirect(url_for('auth_start'))
#     credentials = client.OAuth2Credentials.from_json(session['credentials'])
#     if credentials.access_token_expired:
#         return redirect(url_for('auth_start'))
#     else:
#         # http_auth = credentials.authorize(httplib2.Http())
#         # DRIVE_SERVICE = discovery.build('drive', 'v3', http_auth)
#         # files = DRIVE_SERVICE.files().list().execute()
#         # return json.dumps(files)
#         image_link_list = []
#         for service in cloud_services:
#             folder_name = path
#             folder_name = [unicode.encode(item, 'utf-8') for item in folder_name.split('/')]
#             folder_name.remove(service.name)
#             folder_name = '/'.join(folder_name)
#             link_list = get_cached(folder_name)
#             # if not REFRESH_DONE or link_list is None:
#             image_link_list = DBX.get_files_folder_temp_link_list("/" + folder_name)
#             # cache(path, link_list)
#             # else:
#             #     print "from cache"
#             # image_link_list = image_link_list + link_list
#         return render_template(CONF.index, dict=TREE,
#                                folder_name=folder_name,
#                                image_link=image_link,
#                                image_link_list=image_link_list)
#
#


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='favicon.ico')


@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(**TREE)


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if not CONNECTED:
        if request.method == 'POST':
            return redirect(url_for('auth_start'))
        else:
            return render_template('connect.html')
    else:
        return redirect(url_for('main'))


@app.route('/auth-start')
def auth_start():
    authorize_url = get_auth_flow().start()
    return redirect(authorize_url)


def get_auth_flow():
    return DropboxOAuth2Flow(CONF.app_key, CONF.app_secret, CONF.redirect_uri,
                             session, CONF.csrf_token)


@app.route('/<service>-auth-finish', methods=['GET'])
def auth_finish():
    global CONNECTED
    global DBX
    global TREE
    try:
        access_token, user_id, url_state = \
                get_auth_flow().finish(request.args)
        DBX = Dropbox(access_token)
        # TREE = DBX.get_dict_folders()
        CONNECTED = True
        # TREE = {}
        for service in cloud_services:
            TREE[service.name] = service.get_dict_folders()
        return redirect("/")
    except oauth.BadRequestException as e:
        return redirect(url_for(error, code=404))
    except oauth.BadStateException as e:
        return redirect(url_for("auth_start"))
    except oauth.CsrfException as e:
        return redirect(url_for(error, code=403))
    except oauth.NotApprovedException as e:
        return redirect(url_for("main"))
    except oauth.ProviderException as e:
        print("Auth error: %s" % (e,))


@app.route('/error/<code>')
def error(code):
    d = {
        "400": "Bad Request",
        "403": "Forbidden",
        "404": "Not found!",
    }
    return render_template('error.html', message=d[code])

def get_cached(data):
    h = hashlib.md5()
    h.update(data)
    h = h.digest()
    return DB.get_list(data)


def cache(key, value):
    h = hashlib.md5()
    h.update(key)
    h = h.digest()
    DB.set(key, value, 4* 60 * 60)


class Cache(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        refresh_cache()
        print "REFRESH DONE"


def refresh_cache():
    global REFRESH_DONE
    for service in cloud_services:
        files = service.get_all_files()
        for f in files:
            p = f.path_lower
            l = p.split('/')
            if service.is_photo(f.path_lower):
                temp_link = service.get_temp_link(p)
                DB.append_to_list('/'.join(l[1:-1]), temp_link)
        REFRESH_DONE = True

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args()
    CONF = config.compute_config(parsed_arguments.config, "web_app")
    app.secret_key = CONF.secret_key
    app.jinja_env.add_extension('jinja2.ext.do')
    # if CONNECTED:
    #     DB = Redis.DB()
    DBX = Dropbox(auth2_token="sad")
    cloud_services = [DBX]
    REFRESH_DONE = False
    TREE = {}
    for service in cloud_services:
        TREE[service.name] = {"": None}
    # thread = Cache()
    # thread.start()

    app.run()


