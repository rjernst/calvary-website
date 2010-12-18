#!/usr/bin/env python

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache

import logging
import common

from common.render import user_tpl
from auth.account import require_login
from school import tpl

class Faculty(db.Model):
    name = db.StringProperty()
    email = db.StringProperty()
    education = db.StringProperty()
    picture = db.StringProperty() # TODO: replace with actual pic blob
    hobbies = db.StringListProperty()
    bio = db.TextProperty()    

class FacultyHandler(webapp.RequestHandler):

    def get(self):
        data = memcache.get('school')
        if data is None or common.debug:
            data = tpl('faculty.html')
            memcache.set('school', data)
        user_tpl(self, data)
        

app = webapp.WSGIApplication([('.*', FacultyHandler),], debug=common.debug)
def main(): run_wsgi_app(app)
if __name__ == "__main__": main()
