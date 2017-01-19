import inspect
import logging
import os
import random
from logging import getLogger

from geopy.distance import vincenty
from googlemaps import Client

from mongotable.mongo_dict import MongoDict, COLLECTION


class DummyClass: pass


class GoogleMap:
    keys = {}
    clients = []

    nyc = {'new york county', 'bronx county', 'kings county', 'new york county', 'queens county', 'richmond county'}

    def __init__(self):
        self.mongo = MongoDict()
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

    def get_client(self) -> Client:
        return random.choice(self.clients)

    def check_if_nyc(self, address) -> str:
        if address is None:
            return "None"
        return str(address.lower() in self.nyc)

    def geocode(self, address):
        if [COLLECTION.GEO_CACHE, address] not in self.mongo:
            value = self.get_client().geocode(address)
            self.mongo.put(COLLECTION.GEO_CACHE, address, value)
            return value
            # self.logger.critical("cached")
        else:
            return self.mongo.get(COLLECTION.GEO_CACHE, address)
            # self.logger.critical("  fetched")


class Tacheometer():
    def __init__(self):
        pass

    def distance(self, d1, d2):
        return vincenty(d1, d2).miles