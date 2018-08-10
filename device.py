from mongoengine import *

class Device(Document):
  mac = StringField()
  description = StringField()
  enabled = BooleanField()
  status = DictField()
  date = DateTimeField()
 