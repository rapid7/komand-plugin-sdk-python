import komand.message  as message
import sys
import logging
import requests
import os


class Stdout(object):
    """ stdout dispatcher """
    def __init__(self, config={}):
        self.webhook_url = config.get('webhook_url')
        self.custom_encoder = config.get("custom_encoder")
        self.custom_decoder = config.get("custom_decoder")

    def write(self, msg):
        message.marshal(msg, sys.stdout, ce=self.custom_encoder)

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
        try:
            r = requests.post(self.url, 
                json=msg, 
                verify=os.environ['SSL_CERT_FILE'])
            logging.info('POST %s returned %s', self.url, r.content)
        except Exception as ex:
            logging.error('ERROR: POST to %s failed. CA bundle path: %s Exception %s',
                self.url,
                os.environ['SSL_CERT_FILE'],
                str(ex))

