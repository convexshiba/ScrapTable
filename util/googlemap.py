import inspect
import logging
import os
import random
from logging import getLogger

from googlemaps import Client


class DummyClass: pass


class GoogleMap:
    keys = {}
    clients = []

    nyc = {'new york county', 'bronx county', 'kings county', 'new york county', 'queens county', 'richmond county'}

    def __init__(self):

        self.logger = getLogger("GoogleMap")
        getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.ERROR)

        file = os.path.join(os.path.dirname(os.path.abspath(inspect.getsourcefile(DummyClass))), 'api.key')
        # dynamically load key from api.key
        with open(file) as f:
            for line in f:
                [app_name, app_key] = line.strip().split(" ")
                self.logger.info("Found api key:" + app_key)

                self.keys[app_name] = app_key
                self.clients.append(Client(key=app_key,
                                           timeout=None,
                                           retry_timeout=40))

                self.logger.info("Registered api key:" + app_key)

    def get_client(self):
        return random.choice(self.clients)

    def is_nyc(self, address):
        if address is None:
            return "None"
        return str(address.lower() in self.nyc)

    def geocode(self, address):
        return self.get_client().geocode(address)
