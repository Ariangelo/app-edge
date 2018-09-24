from mongoengine import *

class User(Document):
  login = StringField(max_length=30)
  password = StringField(max_length=30)
  level = StringField()
  email = EmailField(max_length=30)
  name = StringField(max_length=30)
  
class Device(Document):
  mac = StringField()
  description = StringField()
  enabled = BooleanField()
  status = DictField()
  type = IntField()
  infos = ListField()
  date = DateTimeField()
  _class = StringField()
  
class Scene(Document):
  description = StringField()
  enabled = BooleanField()
  devices = StringField()
  _class = StringField()