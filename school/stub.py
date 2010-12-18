
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.template import render
from google.appengine.api import memcache

import common
from common.render import user_tpl
from school import tpl

class Stub(webapp.RequestHandler):
    def get(self):
        data = memcache.get('school')
        if data is None or common.debug:
            page = self.request.path[8:].capitalize()
            data = tpl('stub.html', { 'page': page })
            memcache.set('school', data)
        user_tpl(self, data)

app = webapp.WSGIApplication([('/school.*', Stub),], debug=common.debug)
def main(): run_wsgi_app(app)
if __name__ == "__main__": main()
