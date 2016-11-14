import dropbox
from ParseEnvironment import Parser
import requests
import time
from lib.DataStructures.Tree import *

class Dropbox:
    def __init__(self):
        parser = Parser()
        self.token = Parser.token
        self.dbx = dropbox.Dropbox(self.token)
        self.obj = {}
        for item in self.get_all_files():
            self.obj[item.path_lower] = item

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

    @classmethod
    def is_folder(cls, item):
        return type(item) is dropbox.files.FolderMetadata

    def get_files(self, path=None):
        if path is None:
            return self.dbx.files_list_folder('', recursive=False).entries
        list = []
        for item in self.dbx.files_list_folder("{path}".format(path=path), recursive=False).entries:
            list.append(str(item.path_lower))
        return list

    def get_all_files_folder(self, path):
        list = []
        for file in self.get_files(path):
            if "." in file:
                list.append(file)
        return list

    def files_path(self, path=None):
        if path is None:
            result = self.get_files()
        else:
            result = self.get_files(path)

    def path_to_dict(self, path):
        path_list = str(path).split('/')[1:]
        before = None
        for item in path_list[::-1]:
            dictionary = {}
            dictionary[item] = before
            before = dictionary.copy()
        return dictionary

    def get_temp_link(self, path):
        return str(self.dbx.files_get_temporary_link(path).link)

    def get_dict_files(self):
        tree = Tree()
        for item in self.get_all_files():
            path = self.process_path(item)
            tree.process_path(item.path_lower)
        return tree.dictionary

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
            list.append(self.get_temp_link(item))
        return list