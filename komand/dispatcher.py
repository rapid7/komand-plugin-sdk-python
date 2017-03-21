import komand.message  as message
import sys
import logging
import requests

class Noop(object):
    def __init__(self, config={}):
        self.msg = None

    def write(self, msg):
        self.msg = msg

class Stdout(object):
    """ stdout dispatcher 
    actually can support any stream now
    """
    def __init__(self, config={}, stream=sys.stdout):
        self.webhook_url = config.get('webhook_url')
        self.custom_encoder = config.get('custom_encoder')
        self.custom_decoder = config.get('custom_decoder')
        self.stream = stream or sys.stdout

    def write(self, msg):
        message.marshal(msg, self.stream, ce=self.custom_encoder)

class Http(object):
    """ HTTP dispatcher """
    def __init__(self, config={}):
        if not config:
            raise ValueError('missing HTTP dispatcher config')

        if not config.get('url'):
            raise ValueError('missing HTTP dispatcher config url')

        self.url = config['url']
        self.webhook_url = config.get('webhook_url')
        self.custom_encoder = config.get("custom_encoder")
        self.custom_decoder = config.get("custom_decoder")

        logging.info('Using dispatcher config: %s', config)

    def write(self, msg):
        r = requests.post(self.url, json=msg)
        logging.info('POST %s returned %s', self.url, r.content)
