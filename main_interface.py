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
from lib.cloud_storage.dropbox_ import Dropbox
from lib.cloud_storage.GooglePhotos import GooglePhotos

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

TREE = None
DB = None
REFRESH_DONE = None
CONNECTED = None

modules_path = {
    'Dropbox': 'lib.cloud_storage.dropbox_'
}


@app.route('/')
def home():
    # if 'credentials-google' not in session:
    #     return redirect(url_for('auth_finish'))
    l = [item for item in TREE.keys() if TREE[item] == {"": None}]
    try:
        return render_template('connect.html', dict=TREE,
                               folder_name='home',
                               services_list=l,
                               error_message=request.args['error_message'])
    except KeyError:
        return render_template('connect.html', dict=TREE,
                               folder_name='home',
                               services_list=l)


@app.route('/<path:path>')
def main(path, image_link=None):
    service = unicode.encode(path.split('/')[0], 'utf-8').title()
    # service = Dropbox.name
    if TREE[service] is not None:
        image_link_list = []
        folder_name = path
        folder_name = [unicode.encode(item, 'utf-8') for item in folder_name.split('/')]
        folder_name.remove(service)
        folder_name = '/'.join(folder_name)
        # link_list = get_cached(folder_name)
        # if not REFRESH_DONE or link_list is None:
        print folder_name
        try:
            image_link_list = cloud_services[service].get_files_folder_temp_link_list("/" + folder_name)
        except:
            error_message = "Error! Folder '%s' from '%s' does not exist!" % \
                            (folder_name.split('/')[-1],'/'.join(folder_name.split('/')[:-1]))
            return redirect(url_for('home', error_message=error_message))
                # cache(path, link_list)
        # else:
        #     print "from cache"
        # image_link_list = image_link_list + link_list
        print "TREE:",TREE
        return render_template(CONF.index, dict=TREE,
                               folder_name=folder_name,
                               image_link=image_link,
                               image_link_list=image_link_list)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='favicon.ico')


@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(**TREE)


@app.route('/Dropbox-auth-start')
def auth_start():
    # service = unicode.encode(service, 'utf-8').title()
    # module = __import__(modules_path[service], fromlist=['cloud_storage'])
    # class_ = getattr(module, service)
    authorize_url = get_dropbox_auth_flow().start()
    return redirect(authorize_url)


@app.route('/Dropbox-auth-finish', methods=['GET'])
def dropbox_auth_finish():

    from dropbox import oauth
    try:
        service = Dropbox.name
        access_token, user_id, url_state = \
            get_dropbox_auth_flow().finish(request.args)
        cloud_services[service] = Dropbox(access_token)
        # TREE[service] = cloud_services[service].get_dict_folders()['FloatingOcean']
        TREE[service] = cloud_services[service].get_dict_folders()
        return redirect(url_for('home'))
    except oauth.BadRequestException as e:
        return redirect(url_for(error, code=404))
    except oauth.BadStateException as e:
        return redirect("/Dropbox-auth-start")
    except oauth.CsrfException as e:
        return redirect(url_for(error, code=403))
    except oauth.NotApprovedException as e:
        return redirect(url_for("home"))
    except oauth.ProviderException as e:
        print("Auth error: %s" % (e,))


def get_dropbox_auth_flow():
    from dropbox import  DropboxOAuth2Flow
    return DropboxOAuth2Flow(CONF.app_key, CONF_dropbox.app_secret, CONF_dropbox.redirect_uri,
                             session, CONF_dropbox.csrf_token)

@app.route('/Gdrive-auth-start')
def google_auth_start():
    if 'credentials-google' not in session:
        return redirect(url_for('google_auth_finish'))
    credentials = client.OAuth2Credentials.from_json(session['credentials-google'])
    if credentials.access_token_expired:
        return redirect(url_for('google_auth_finish'))
    else:
        return redirect(url_for('google_auth_finish'))

@app.route('/google-auth-finish')
def google_auth_finish():
    secrets_path = os.path.join(os.path.abspath(os.path.curdir), 'config', 'client_secret.json')
    secrets_path = 'D:\\faculta\\Licenta\\rpi\\config\\client_secret.json'
    flow = client.flow_from_clientsecrets(
        secrets_path,
        scope='https://www.googleapis.com/auth/drive.readonly',
        redirect_uri=url_for('google_auth_finish', _external=True))
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        service = GooglePhotos.name
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials-google'] = credentials.to_json()
        cloud_services[service] = GooglePhotos(credentials)
        TREE[service] = cloud_services[service].get_dict_folders()
        return redirect(url_for('home'))


@app.route('/error')
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
            p = service.get_item_path(f)
            l = p.split('/')
            if service.is_photo(service.get_item_path(f)):
                temp_link = service.get_temp_link(p)
                DB.append_to_list('/'.join(l[1:-1]), temp_link)
        REFRESH_DONE = True


def get_all_routes():
    for rule in app.url_map.iter_rules():
        print rule, rule.endpoint, rule.arguments

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args()
    CONF = config.compute_config(parsed_arguments.config, "web_app")
    app.secret_key = CONF.secret_key
    CONF_dropbox = config.compute_config(parsed_arguments.config, "dropbox")
    app.jinja_env.add_extension('jinja2.ext.do')
    # if CONNECTED:
    #     DB = Redis.DB()
    cloud_services = {Dropbox.name: None,
                      GooglePhotos.name: None}
    REFRESH_DONE = False
    TREE = {}
    for service in cloud_services:
        TREE[service] = {"": None}
    # cloud_services[Dropbox.name] = Dropbox(auth2_token="das")
    # TREE[service] = cloud_services[service].get_dict_folders()
    # thread = Cache()
    # thread.start()
    get_all_routes()
    app.run()
