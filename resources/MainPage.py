import webapp2
import jinja2
import os
from resources.TemplateRender import TemplateRender
from lib.CloudStorage.Dropbox import Dropbox



class MainPage(TemplateRender):

    def get(self):
        dbx = Dropbox()
        tree = dbx.get_dict_files()
        self.render('index.html', my_list = [1, 2, 3, 4], dict=tree,
                    link="https://d1ra4hr810e003.cloudfront.net/media/27FB7F0C-9885-42A6-9E0C19C35242B5AC/0/D968A2D0-35B8-41C6-A94A0C5C5FCA0725/F0E9E3EC-8F99-4ED8-A40DADEAF7A011A5/dbe669e9-40be-51c9-a9a0-001b0e022be7/thul-IMG_2100.jpg")


#
#     # tree = dbx.get_dict_files()
#     # print tree
#     def get(self):
#         return render_template('index.html', my_list=[1,2,3,4], dict=tree,
#                            link="https://d1ra4hr810e003.cloudfront.net/media/27FB7F0C-9885-42A6-9E0C19C35242B5AC/0/D968A2D0-35B8-41C6-A94A0C5C5FCA0725/F0E9E3EC-8F99-4ED8-A40DADEAF7A011A5/dbe669e9-40be-51c9-a9a0-001b0e022be7/thul-IMG_2100.jpg")
