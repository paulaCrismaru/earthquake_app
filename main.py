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

import re

from flask import Flask
from flask import jsonify
from flask import render_template
from lib.CloudStorage.Dropbox import Dropbox

app = Flask(__name__)

DBX = Dropbox()
TREE = DBX.get_dict_folders()

CONNECTED = True
INDEX = "index.html"

@app.route("/")
def main():
    if CONNECTED:
        return render_template(INDEX, dict=TREE, image_list=[1,2,3])

@app.route('/folders/<path:path>', methods=['GET'])
def files(path, folder_name=None, image_link="http://placehold.it/400x300"):
    print(path)
    folder_name = path
    image_link_list = DBX.get_files_folder_temp_link_list("/" + path)
    return render_template(INDEX, dict=TREE,
                           folder_name=folder_name,
                           image_link=image_link,
                           image_link_list=image_link_list)


@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(**TREE)

if __name__ == "__main__":
    app.run()
    DBX = Dropbox()
    TREE = DBX.get_dict_folders()
    print(TREE)