#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
import plugins.blog
import logging

_data = []
_data.append(('/data/blog/articles', plugins.blog.ArticlesHandler))
_data.append(('/data/blog/tags', plugins.blog.TagsHandler))
_application = webapp.WSGIApplication(_data, debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(_application)

if __name__ == '__main__':
  main()
