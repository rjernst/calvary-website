
from google.appengine.ext import webapp
from base.render import render

class StaticHandler(webapp.RequestHandler):
    def get(self):
        render(self, None, {})
