from datetime import datetime as dt
import os
import time

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

class MongoDB(object):
    """
    Wrapper for MongoDB connection - provides methods to connect and recreate the DB/indexes
    """

    def __init__(self):
        self.client = None

    def connect(self):
        """
        Connect to mongodb and return db
        """
        host, port = os.environ['MONGO_HOST'], int(os.environ['MONGO_PORT'])

        # Keep trying to connect until it succeeds
        connected = False
        self.client = MongoClient(host, port, serverSelectionTimeoutMS=10, connectTimeoutMS=20000)
        while not connected:
            try:
                # Test if actually connected
                self.client.server_info()
                print('Successfully connected to DB')
                connected = True
            except ServerSelectionTimeoutError:
                print('Couldn\'t connect to DB - retrying...')
                time.sleep(1)

        return self.client.Fumble

    def recreate(self):
        """
        Drop database and recreate indexes
        """
        if not self.client:
            self.connect()

        # Drop if exists
        self.client.drop_database('Fumble')

        # Create DB
        db = self.client.Fumble

        # Since user_locations gets written to by lots of devices every second,
        # set TTLs for these records so they expire 30 seconds after getting created.
        user_locs = db.user_locations
        user_locs.create_index("time", expireAfterSeconds=30)

        # Let's create a 2d index on the "loc" field so
        # we can perform geospatial queries
        user_locs.create_index([("loc", "2dsphere")])
