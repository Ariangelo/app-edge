#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.defer import inlineCallbacks

from datetime import datetime
from mongoengine import connect

import binascii
import bson

from model import User, Device

PREFIX = u'io.robotica.controle'

class ControleBackend(ApplicationSession):
  def __init__(self, config):
    ApplicationSession.__init__(self, config)
    self.payload = {}
    self.user = User()
    self.device = Device()
    self.statusDevice = {}
    self.init()

  def mongoConnect(self, _db, _payload):
    self.client = connect(
      db = _db, 
      host = 'ds227119.mlab.com',
      port = 27119, 
      username = _payload[user], 
      password = _payload[password]
    )

  def init(self):
    devices = [];
    for device in Device.objects:
      if device.enabled : 
        self.statusDevice[device.mac] = device.status
        devices.append(device.mac)
    self.log.info('Dispositivos atualizados: {}'.format(devices))    
    
    '''
    self.statusDevice = {
      "b827eb160a65": {"d": {"o": [[0, 6, 0, 0], [1, 6, 0, 0], [2, 6, 0, 0]], "i": [[0, 13, 0, 1], [1, 13, 0, 1], [7, 13, 0, 1]]}},
      "2bea2300": {"d": {"o": [[14, 0]], "i": [[-1, 2, 1, 0], [-1, 16, 0, 0], [1, 10, 0, 0]]}}, 
      "8d6fef00": {"d": {"o": [[14, 0]], "i": [[-1, 1, 1, 1], [-1, 3, 1, 1], [-1, 15, 1, 1]]}}
    }
    ''' 

  @wamp.register(u'{}.login'.format(PREFIX))
  def submitLogin(self, subject):
    self.payload = bson.BSON.decode(binascii.unhexlify(subject))
    self.log.info("login to: {}".format(self.payload[user]))
    self.mongoConnect('edge', payload)
    return subject

  @wamp.register(u'{}.status'.format(PREFIX))
  def submitStatus(self, subject):
    if self.statusDevice.get(subject) is None:
      self.statusDevice[subject] = {"d":{"o": [[0, 6, 0, 0], [1, 6, 0, 0], [2, 6, 0, 0]], "i": [[0, 13, 0, 1], [1, 13, 0, 1], [2, 13, 0, 1]]}}
    self.log.info("status : {} = {}".format(subject, self.statusDevice.get(subject))),
    return self.statusDevice.get(subject)

  @wamp.register(u'{}.load'.format(PREFIX))
  def submitLoad(self):
    self.log.info("load : {}".format(self.statusDevice))
    self.publish(u'io.robotica.controle.on_digital', self.statusDevice)
    return self.statusDevice

  @wamp.register(u'{}.digital'.format(PREFIX))
  def submitDigital(self, subject):
    device = subject.get('i')
    self.statusDevice[device] = subject.get('v')
    self.log.info("change : {} = {}".format(device, self.statusDevice[device]))
    self.publish(u'io.robotica.controle.on_{}'.format(device), self.statusDevice[device])
    self.publish(u'io.robotica.controle.on_digital', self.statusDevice)
    
    #Write to Mongodb last status of device
    deviceDB = Device.objects(mac = device).get()
    deviceDB.date = datetime.now()
    deviceDB.status = self.statusDevice[device]
    deviceDB.save()
    return subject
    
  @inlineCallbacks
  def onJoin(self, details):
    res = yield self.register(self)
    self.log.info("ControleBackend: {} procedimentos registrados!".format(len(res)))

  def main():
    # Crossbar.io connection configuration
    url = os.environ.get('CBURL', u'ws://localhost:8080/ws')
    realm = os.environ.get('CBREALM', u'crossbarRobotica')

    # parse command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output.')
    parser.add_argument('--url', dest='url', type=six.text_type, default=url, help='The router URL (default: "ws://localhost:8080/ws").')
    parser.add_argument('--realm', dest='realm', type=six.text_type, default=realm, help='The realm to join (default: "crossbarRobotica").')

    args = parser.parse_args()

    # start logging
    #if args.debug:
    txaio.start_logging(level='debug')
    #else:
    #  txaio.start_logging(level='info')

    # any extra info we want to forward to our ClientSession (in self.config.extra)
    extra = {
      u'foobar': u'A custom value'
    }

    # now actually run a WAMP client using our session class ClientSession
    runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra)
    runner.run(ControleBackend, auto_reconnect=True)

if __name__ == "__main__":
  main()
