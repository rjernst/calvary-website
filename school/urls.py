#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
import base.static
from base.render import Link
import school.home

links = [
    Link('/school', 'Home', school.home.HomeHandler),
    Link('/school/about', 'About', base.static.StaticHandler),
    Link('/school/admissions', 'Admissions', base.static.StaticHandler),
    Link('/school/classes', 'Classes', base.static.StaticHandler),
    Link('/school/faculty', 'Faculty', base.static.StaticHandler),
    Link('/school/programs', 'Programs', base.static.StaticHandler),
    Link('/school/parents', 'Parents', base.static.StaticHandler),
]

_handlers = [(link.url, link.handler) for link in links]
#_handlers.append(('/school', school.home.HomeHandler))
_application = webapp.WSGIApplication(_handlers, debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(_application)

if __name__ == '__main__':
  main()
