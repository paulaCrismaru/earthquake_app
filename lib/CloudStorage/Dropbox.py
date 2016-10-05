import dropbox
from ParseEnvironment import Parser
# from dropbox import dropbox
from dropbox import DropboxOAuth2Flow
import requests
import json
import time
import codecs
from DataStructures.Tree import *

class Dropbox:
    def __init__(self):
        parser = Parser()
        self.token = Parser.token
        # self.token = "your token here"
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

    def stream(self):
        for item in self.get_all_files():
            if item.name == "Metal Cat.mp4":
                break

        response = self.dbx.files_get_temporary_link("/Metal Cat.mp4")
        url = response.link

        request = requests.get(url, stream=True)
        while request.status_code != 200:
            print "*"
            time.sleep(1)

           # do some sort of things
        # d.files_get_temporary_link("/Metal Cat.mp4")

    def get_files(self, path=None):
        """ returns files in folder.
        folder is a complete path to the folder"""
        if path is None:
            return self.dbx.files_list_folder('', True).entries
        list = []
        for item in self.dbx.files_list_folder("{path}".format(path=path), True).entries:
            list.append(str(item.path_lower))
        return list

    def files_path(self, path=None):
        if path is None:
            result = self.get_all_files()
        else:
            result = self.get_files_folder(path)

    def path_to_dict(self, path):
        path_list = str(path).split('/')[1:]
        before = None
        for item in path_list[::-1]:
            dictionary = {}
            dictionary[item] = before
            before = dictionary.copy()
        return dictionary

    # @classmethod
    def get_temp_link(self, path):
        return self.dbx.files_get_temporary_link(path)

    def get_dict_files(self):
        tree = Tree()
        for item in self.get_all_files():
            path = self.process_path(item)
            tree.process_path(item.path_lower)
        return tree.tree

    def get_dict_folders(self):
        tree = Tree()
        for item in self.get_all_files():
            if self.is_folder(item):
                path = self.process_path(item)
                tree.process_path(item.path_lower)
        # return tree.get_dict()
                return {
                    "folder1":{
                        "folder12":{}
                    },
                    "folder2":{
                        "folder21":{
                            "folder211":{}
                        },
                        "folder22": {
                            "folder221":{ },
                            "folder222":{"folder2221":{}}
                        }
                    }

                }

if __name__ == "__main__":
    list = []
    db = Dropbox()
    # t = Tree()
    # for item in db.get_all_files():
    #     # print item
    #     path = item.path_lower
    #     l = str(path).split('/')[1:]
    #     t.process_path(l)
    # print db.obj
        # print item.path_lower, db.path_to_dict(item.path_lower)

    # print db.get_files_folder("pisici")





    # for item in db.get_files_folder("curs festiv"):
    #     print item.path_lower