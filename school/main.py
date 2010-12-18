
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.template import render
from google.appengine.api import memcache

import common
from common.render import user_tpl
from auth.account import require_login
from school import tpl

class Home(webapp.RequestHandler):
    @require_login
    def get(self):
        data = memcache.get('school')
        if data is None or common.debug:
            data = tpl('home.html')
            memcache.set('school', data)
        user_tpl(self, data)

app = webapp.WSGIApplication([('/school', Home),], debug=common.debug)
def main(): run_wsgi_app(app)
if __name__ == "__main__": main()
