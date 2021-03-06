#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.dao.document import Collection
from valarie.controller.messaging import add_message
from valarie.view.auth import login_view

SESSION_KEY = '_cp_username'

def check_credentials(username, password):
    inventory = Collection("inventory")
    
    for user in inventory.find(name=username,type="user"):
        if user.object["enabled"] in ('false', False):
            return "User {0} is disabled!".format(username)
        if user.object["password"] == password:
            return None
        else:
            return "Incorrect password!"
    
    return "User {0} does not exist!".format(username)

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
                    
        else:
            raise cherrypy.HTTPRedirect("/auth/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check

class Auth(object):
    def on_login(self, username):
        inventory = Collection("inventory")
        
        for user in inventory.find(sessionid=cherrypy.session.id,type="user"):
            user.object['sessionid'] = None
            user.set()
        
        for user in inventory.find(name=username,type="user"):
            user.object['sessionid'] = cherrypy.session.id
            user.set()

    def on_logout(self, username):
        pass
    
    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return login_view()
        
        error_msg = check_credentials(username, password)
        if error_msg:
            return login_view()
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")
    
    @cherrypy.expose
    @require()
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")
