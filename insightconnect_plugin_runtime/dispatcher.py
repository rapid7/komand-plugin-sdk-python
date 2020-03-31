# -*- coding: utf-8 -*-
import json
import logging
import os
import requests
import sys


class Noop(object):
    def __init__(self, config={}):
        self.msg = None
        self.webhook_url = ""

    def write(self, msg):
        self.msg = msg


class Stdout(object):
    """
    stdout dispatcher.
    actually can support any stream now
    """

    def __init__(self, config={}, stream=sys.stdout):
        self.webhook_url = config.get("webhook_url")
        self.custom_encoder = config.get("custom_encoder")
        self.custom_decoder = config.get("custom_decoder")
        self.stream = stream or sys.stdout

    def write(self, msg):
        json.dump(msg, self.stream, cls=self.custom_encoder)
        self.stream.flush()


class Http(object):
    """ HTTP dispatcher """

    def __init__(self, config={}):
        if not config:
            raise ValueError("missing HTTP dispatcher config")

        if not config.get("url"):
            raise ValueError("missing HTTP dispatcher config url")

        self.url = config["url"]
        self.webhook_url = config.get("webhook_url")
        self.custom_encoder = config.get("custom_encoder")
        self.custom_decoder = config.get("custom_decoder")

        logging.info("Using dispatcher config: %s", config)

    def write(self, msg):
        try:
            r = requests.post(self.url, json=msg, verify=os.environ["SSL_CERT_FILE"])
            logging.info("POST %s returned %s", self.url, r.content)
        except Exception as ex:
            logging.error(
                "ERROR: POST to %s failed. CA bundle path: %s Exception %s",
                self.url,
                os.environ["SSL_CERT_FILE"],
                str(ex),
            )
