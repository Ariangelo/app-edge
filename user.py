from mongoengine import *

class User(Document):
  login = StringField(max_length=30)
  password = StringField(max_length=30)
  level = StringField()
  email = EmailField(max_length=30)
  name = StringField(max_length=30)