from lib.base_cloud_storage import BaseCloudStorage
from lib.CloudStorage.ParseEnvironment import Parser
from lib.DataStructures.Tree import *
import dropbox


class Dropbox(BaseCloudStorage):
    def __init__(self, auth2_token=None):
        BaseCloudStorage.__init__(self)
        self.auth(auth2_token)
        self.name = 'Dropbox'

    def auth(self, auth2_token):
        if auth2_token is not None:
            self.dbx = dropbox.Dropbox(auth2_token)

    def get_all_files(self):
        return self.dbx.files_list_folder('', True).entries

    def process_path(self, item):
        if Dropbox.is_folder(item):
            return item.path_lower + "/"
        return item.path_lower

    def get_current_account(self):
        return self.dbx.users_get_current_account()

    def get_folders(self):
        return (item for item in self.get_all_files() if self.is_folder(item))

    @staticmethod
    def is_folder(item):
        return type(item) is dropbox.files.FolderMetadata

    def get_files(self, path=None):
        if path is '/':
            return [item for item in self.dbx.files_list_folder('', recursive=False).entries
                    if "." in item.path_lower]
        list = []
        for item in self.dbx.files_list_folder("{path}".format(path=path), recursive=False).entries:
            list.append(item)
        return list

    def get_all_files_folder(self, path):
        list = []
        for item in self.get_files(path):
            if self.is_photo(item.path_lower):
                list.append(item)
        return list

    def get_temp_link(self, path):
        return str(self.dbx.files_get_temporary_link(path).link)

    def get_dict_folders(self):
        tree = Tree()
        for item in self.get_all_files():
            if self.is_folder(item):
                path = self.process_path(item)
                tree.process_path(item.path_lower)
        return tree.dictionary

    def get_files_folder_temp_link_list(self, path):
        list = []
        for item in self.get_all_files_folder(path):
            list.append(self.get_temp_link(item.path_lower))
        return list
