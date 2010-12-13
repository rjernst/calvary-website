
from google.appengine.ext import db, webapp
from google.appengine.api import users
from django.utils import simplejson as json

class UserInfo(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    email = db.EmailProperty()
    groups = db.ListProperty(int)

# TODO: rethink this...maybe permissions should be part of each section?
class Group:
    staff = 1
    teacher = 2
    parent = 3
    student = 4


