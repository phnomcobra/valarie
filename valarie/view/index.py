#!/usr/bin/python

import jinja2
    
def index_view():
    templateLoader = jinja2.FileSystemLoader(searchpath = "./valarie/view/templates")
    templateEnv = jinja2.Environment(loader = templateLoader)
    template = templateEnv.get_template('index2.html')
    return template.render()
    