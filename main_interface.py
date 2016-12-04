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
    request, render_template, jsonify
from lib.CloudStorage.Dropbox import Dropbox
from dropbox import DropboxOAuth2Flow, oauth

app = Flask(__name__)

CONNECTED = None
DBX = None
TREE = None


@app.route("/")
def main():
    if CONNECTED:
        return render_template(CONF.index, dict=TREE)
    else:
        return redirect(url_for('connect'))


@app.route('/folders/<path:path>', methods=['GET'])
def files(path, folder_name=None, image_link=None):
    if not CONNECTED:
        return redirect(url_for('connect'))
    folder_name = path
    image_link_list = DBX.get_files_folder_temp_link_list("/" + path)
    return render_template(CONF.index, dict=TREE,
                           folder_name=folder_name,
                           image_link=image_link,
                           image_link_list=image_link_list)


@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(**TREE)


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if not CONNECTED:
        if request.method == 'POST':
            return redirect(url_for('dropbox_auth_start'))
        else:
            return render_template('connect.html')
    else:
        return redirect(url_for('main'))


@app.route('/dropbox-auth-start')
def dropbox_auth_start():
    authorize_url = get_dropbox_auth_flow().start()
    return redirect(authorize_url)


def get_dropbox_auth_flow():
    return DropboxOAuth2Flow(CONF.app_key, CONF.app_secret, CONF.redirect_uri,
                             session, CONF.csrf_token)


@app.route('/dropbox-auth-finish', methods=['GET'])
def dropbox_auth_finish():
    global CONNECTED
    global DBX
    global TREE
    try:
        access_token, user_id, url_state = \
                get_dropbox_auth_flow().finish(request.args)
        DBX = Dropbox(access_token)
        TREE = DBX.get_dict_folders()
        CONNECTED = True
        return redirect("/")
    except oauth.BadRequestException as e:
        return redirect(url_for(error, code=404))
    except oauth.BadStateException as e:
        return redirect(url_for("dropbox_auth_start"))
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

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args()
    CONF = config.compute_config(parsed_arguments.config, "web_app")
    CONNECTED = False
    app.secret_key = CONF.secret_key
    app.run()

