import json

import flask
import httplib2

from apiclient import discovery
from lib.DataStructures.Tree import *
from oauth2client import client
import os

from lib.base_cloud_storage import BaseCloudStorage
app = flask.Flask(__name__)


class GooglePhotos(BaseCloudStorage):
    name = "Gdrive"
    def __init__(self, auth2_token=None):
        BaseCloudStorage.__init__(self, auth2_token)
        self.auth(auth2_token)
        self.email = None
        self.map = {}
        self.list_path_child = None

    def auth(self, credentials):
        # credentials = client.OAuth2Credentials.from_json(args['credentials-google'])
        http_auth = credentials.authorize(httplib2.Http())
        self.drive_service = discovery.build('drive', 'v2', http_auth)
        files = self.drive_service.files().list().execute()

    def get_all_files(self):
        return self.drive_service.files().list().execute()

    @staticmethod
    def process_path(item):
        return '/'.join(item)

    @staticmethod
    def is_folder(item):
        return item.get(u'mimeType') == 'application/vnd.google-apps.folder'.decode('utf-8')

    def get_list_path_child(self):
        if self.list_path_child is None:
            self.list_path_child = {}
            d_parent_file = {'title': 'FloatingOcean', 'id': None, 'url': None}
            child_list = self.compute_list_path_child(d_parent_file)
            for item in child_list:
                path = self.list_dicts_to_path(item)
                index = len(path.split('/'))
                try:
                    self.list_path_child[path.encode('utf-8')] = \
                        self.list_path_child[path.encode('utf-8')] + item[index:]
                except KeyError:
                    self.list_path_child[path.encode('utf-8')] = item[index:]
        return self.list_path_child

    def list_dicts_to_path(self, l):
        """ receives list of dictionaries and returns the path
        made from the title of the items from the dictionary"""
        new_list = []
        for item in l:
            new_list.append(item.get('title').encode('utf-8'))
        if self.is_photo((new_list[-1])):
            new_list.pop()
        return self.process_path(new_list)

    def get_dict_folders(self, parent_file='FloatingOcean'):
        """ returns tree dictionary"""
        tree = Tree()
        child_list = self.get_list_path_child()
        for path in child_list:
            tree.process_path('/' + path)
        return tree.dictionary

    def get_files_folder_temp_link_list(self, path):
        path = path[1:]
        files_list = self.get_list_path_child().get(path)
        return [item.get('selfLink').encode('utf-8')
                    for item in files_list]

    def get_user_display_name(self):
        if self.display_name is None:
            self.display_name = self.drive_service.about().get().execute()
        return self.display_name

    def is_owner(self, parent_list):
        for parent in parent_list:
            if parent.get('displayName') == self.get_user_display_name():
                return True
        return False

    def get_parents_file(self, file_id):
        return self.drive_service.parents().list(fileId=file_id).execute()

    def get_user_email(self):
        if self.email is None:
            result = self.drive_service.about().get().execute()
            user_details = result.get(u'user')
            self.email = user_details.get('emailAddress')
        return self.email

    def get_path_item(self, folder_name):
        pass

    def get_folder_child_untrashed(self, folder_name, get_field=None):
        email_address = self.get_user_email()
        query = "'{email}' in owners and trashed=False".format(email=email_address)
        result = self.drive_service.files().list(q=query).execute()
        ids = []
        file_name = folder_name
        id = self.get_folder_id(file_name)
        for item in result.get(u'items'):
            if self.is_parent(item.get(u'parents'), id):
                ids.append(item)
        return ids

    def compute_list_path_child(self, parent_file={'title':'FloatingOcean', 'id':None, 'url':None},
                            x=[], l=[]):
        l.append(parent_file)
        child_list = self.get_folder_child_untrashed(parent_file.get("title").encode('utf-8'))
        for child in child_list:
            try:
                d = {
                    'title': child.get(u'title').encode('utf-8'),
                    'id': child.get(u'id').encode('utf-8'),
                    'selfLink': child.get(u'selfLink').encode('utf-8'),
                    'folder': child.get(u'mimeType').encode('utf-8') == 'application/vnd.google-apps.folder'
                }
                self.compute_list_path_child(d)
            except IndexError:
                x.append(copy.deepcopy(l))
            l.pop()
        return x

    def is_parent(self, parent_list, id_parent):
        for parent in parent_list:
            if parent.get(u'id') == id_parent:
                return True
        return False

    def get_folder_id(self, folder_name):
        email_address = self.get_user_email()
        result = self.drive_service.files().list(q="mimeType='application/vnd.google-apps.folder' and "
                                               "'{email}' in owners and "
                                               "trashed=False and "
                                               "title='{folder_name}'".format(email=email_address,
                                                                              folder_name=folder_name)).execute()
        return result.get(u'items')[0].get(u'id')

DRIVE = None
@app.route('/')
def index():
    global DRIVE
    if 'credentials-google' not in flask.session:
        return flask.redirect(flask.url_for('auth_finish'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials-google'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('auth_finish'))
    else:
        if DRIVE is None:
            DRIVE = GooglePhotos(credentials)

        print DRIVE.get_files_folder_temp_link_list('FloatingOcean/folder_1')
        # d_parent_file = {'title': 'FloatingOcean', 'id': None, 'url': None}
        # d = DRIVE.compute_list_path_child(d_parent_file)
        # print DRIVE.get_files_folder_temp_link_list()
        # for item in d:
        #     print item
        #     print d[item]
        #     print

        return json.dumps({})


@app.route('/google-auth-finish')
def auth_finish():
    secrets_path = os.path.join(os.path.abspath(os.path.curdir), 'config', 'client_secret.json')
    secrets_path = 'D:\\faculta\\Licenta\\rpi\\config\\client_secret.json'
    flow = client.flow_from_clientsecrets(
        secrets_path,
        # scope='https://www.googleapis.com/auth/drive.readonly',
        scope='https://www.googleapis.com/auth/drive.file',
        redirect_uri=flask.url_for('auth_finish', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials-google'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug = False
    app.run()