import message 
import sys
import logging
import requests

class Stdout(object):
    """ stdout dispatcher """
    def write(self, msg):
        message.marshal(msg, sys.stdout)

class Http(object):
    """ HTTP dispatcher """
    def __init__(self, config={}):
        if not config:
            raise ValueError('missing HTTP dispatcher config')

        if not config.get('url'):
            raise ValueError('missing HTTP dispatcher config url')

        self.url = config['url']

        logging.info('Using dispatcher config: %s', config)

    def write(self, msg):
        r = requests.post(self.url, json=msg)
        logging.info('POST %s returned %s', self.url, r.content)
