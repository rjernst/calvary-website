import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from auth import facebook, tpl
from google.appengine.ext import db, webapp
from google.appengine.api import users
from django.utils import simplejson as json
from auth.sessions import get_current_session

from google.appengine.api import users

FB_KEY = '183464395004093'
FB_SECRET = '34fc33154cc39b66900dafeadf313d85'
FB_API = facebook.Facebook(FB_KEY, FB_SECRET)
FB_LOGOUT = '<link rel="stylesheet" type="text/css" media="screen" href="openid.css" />'

class UserInfo(db.Model):
  provider = db.StringProperty()
  name = db.StringProperty()
  email = db.EmailProperty()
  groups = db.ListProperty(int)
  admin = db.BooleanProperty(default=False)

def require_login(method):
  def call(handler):
    user = get_current_user(handler.request)
    if not user:
      logging.info("No user!!")
      # TODO: next should be able to have query parameters
      handler.redirect('/auth/login?next=%s' % handler.request.path)
    else:
      method(handler)
  return call

def get_current_user(request):
  session = get_current_session() 
  if session.has_key('user'):
    return session['user']
  else:
    (user_key, provider) = find_user_key(request)
    if user_key is not None:
      user = UserInfo.get_by_key_name(user_key)
      session.set_quick('user', user)
      return user
   
  return None

def find_user_key(request):
  guser = users.get_current_user()
  key = None
  provider = None
  if guser is not None:
    logging.info("federated login found")
    # logged in through federated login
    key = guser.federated_identity() or 'TEST_ID' # TEST is for dev server
    provider = guser.federated_provider() or 'TEST_PROVIDER'
  elif FB_API.find_session(request):
    logging.info("facebook login found")
    # logged in through facebook
    # TODO: FB_API should not contain per session info
    key = 'fb_%s' % FB_API.uid
    provider = 'facebook.connect'
  session = get_current_session()
  if session.has_key('counter'):
    session['counter'] += 1
  else:
    session['counter'] = 1
  logging.info("Counter = %d", session['counter'])
  return (key, provider)

def get_logout_url(request, user):
  if user.provider == 'facebook.connect':
    return 'javascript:FB.logout(function(response) { window.location.reload(); })'
  else:
    return users.create_logout_url(request.url)

class View(webapp.RequestHandler):

  def get(self):
    (user_key, provider) = find_user_key(self.request)
    if user_key is None:
      self.redirect('/auth/login?next=/auth/account')
      return

    user = UserInfo.get_by_key_name(user_key)
    if user is None:
      self.redirect('/auth/account/create?next=/auth/account')
      return

    vars = {
      'name': user.name,
      'email': user.email,
      'provider': user.provider,
      'uid': user.key().name(),
      'logout': get_logout_url(self.request, user),
      'fb_key': FB_KEY,
    }
    tpl(self, 'account.html', vars)
      

# TODO: move this somewhere else
# XXX: is this really worth it? probably won't have too many forms
def check_form(handler, args):
  vals = []
  for arg in args:
    val = handler.request.get(arg)
    if val is None:
      handler.redirect(handler.request.url)
      return None
    vals.append(val)
  return vals

class Create(webapp.RequestHandler):
  
  def get(self):
    (user_key, provider) = find_user_key(self.request)
    if user_key is None:
      self.redirect('/auth/login?next=/auth/account/create')
      return

    user = UserInfo.get_by_key_name(user_key)
    if user:
      self.redirect('/auth/account')
      return

    tpl(self, 'create.html')
    
  def post(self):
    (user_key, provider) = find_user_key(self.request)
    user = UserInfo.get_by_key_name(user_key)
    if user:
      self.redirect('/auth/account')
      return

    vals = check_form(self, ['name', 'email'])
    if not vals:
      return

    user = UserInfo(key_name=user_key, provider=provider, name=vals[0], email=vals[1])
    user.put()
    self.redirect('/auth/account')

application = webapp.WSGIApplication([
    ('/auth/account/create', Create),
    ('/auth/account', View),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
