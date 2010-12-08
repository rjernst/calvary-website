#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
import logging

from google.appengine.ext import db, webapp
from google.appengine.api import users
from django.utils import simplejson as json

class Faculty(db.Model):
    name = db.StringProperty()
    email = db.StringProperty()
    education = db.StringProperty()
    picture = db.StringProperty() # TODO: replace with actual pic blob
    hobbies = db.StringListProperty()
    bio = db.TextProperty()    

class FacultyHandler(webapp.RequestHandler):

    def get(self):
        pass
        

def main():
  app = webapp.WSGIApplication(('.*', FacultyHandler), debug=True)
  wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
  main()


