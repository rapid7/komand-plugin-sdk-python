import komand.message  as message
import sys
import logging
import requests

class Stdout(object):
    """ stdout dispatcher """
    def __init__(self, config={}):
        self.webhook_url = config.get('webhook_url')

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
        self.webhook_url = config.get('webhook_url')

        logging.info('Using dispatcher config: %s', config)

    def write(self, msg):
        r = requests.post(self.url, json=msg)
        logging.info('POST %s returned %s', self.url, r.content)
