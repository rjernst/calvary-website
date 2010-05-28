#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
import base.static
from base.render import Link
import church.home

links = [
    Link('/church/welcome', 'Welcome', base.static.StaticHandler),
    Link('/church/services', 'Services', base.static.StaticHandler),
    Link('/church/ministries', 'Ministries', base.static.StaticHandler),
    Link('/church/events', 'Events', base.static.StaticHandler),
    Link('/church/contact', 'Contact', base.static.StaticHandler),
    Link('/church/calendar', 'Calendar', base.static.StaticHandler),
]

_handlers = [(link.url, link.handler) for link in links]
_handlers.append(('/church', church.home.HomeHandler))
_application = webapp.WSGIApplication(_handlers, debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(_application)


if __name__ == '__main__':
  main()
