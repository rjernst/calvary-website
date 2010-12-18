from auth.sessions import SessionMiddleware

import os
COOKIE_KEY = '\xb9\xea\xd4\x04\xf6C@\xfc\x01d\x8a\xa4_\x9e\xc8\xef\xc7\x86\x07\xfd<\xff\x12\xa1\xd9\xb6\xbb\xf0\x06IFP|67\xd10\xd8]\x16\x85B\x8d\x9cR\x90si\xea\x82\xb9\x19.\x97\x90\x0eI\xcd\x08\x88\xa6\xdc$\xea'

def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
  app = recording.appstats_wsgi_middleware(app)
  return app
