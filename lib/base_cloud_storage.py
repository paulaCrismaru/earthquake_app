from lib.cloud_storage.ParseEnvironment import Parser
from lib.DataStructures.Tree import *
import abc


class BaseCloudStorage(object):
    def __init__(self, auth2_token=None):
        parser = Parser()
        self.auth(auth2_token)

    @abc.abstractmethod
    def auth(self, *args):
        pass

    @abc.abstractmethod
    def get_all_files(self):
        pass

    @abc.abstractmethod
    def process_path(self, item):
        pass

    @abc.abstractmethod
    def get_current_account(self):
        pass

    @abc.abstractmethod
    def get_folders(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def is_folder(item):
        pass

    @abc.abstractmethod
    def get_files(self, path=None):
        pass

    @abc.abstractmethod
    def get_all_files_folder(self, path):
        pass

    @abc.abstractmethod
    def get_temp_link(self, path):
        pass

    @abc.abstractmethod
    def get_dict_folders(self):
        pass

    @abc.abstractmethod
    def get_files_folder_temp_link_list(self, path):
        pass

    # @staticmethod
    # @abc.abstractmethod
    # def get_auth_flow(app_key, app_secret, redirect_uri, session, csrf_token):
    #     pass

    def files_path(self, path=None):
        if path is None:
            result = self.get_files()
        else:
            result = self.get_files(path)

    @staticmethod
    def path_to_dict(path):
        path_list = str(path).split('/')[1:]
        before = None
        for item in path_list[::-1]:
            dictionary = {}
            dictionary[item] = before
            before = dictionary.copy()
        return dictionary

    def get_dict_files(self):
        tree = Tree()
        for item in self.get_all_files():
            # path = self.process_path(item)
            tree.process_path(self.get_item_path(item))
        return tree.dictionary

    @staticmethod
    @abc.abstractmethod
    def get_item_path(item):
        pass

    @staticmethod
    def is_photo(path):
        try:
            _, extension = path.split('.')
            extensions = ['jpg', 'jpeg']
            return extension in extensions
        except ValueError:
            return False
