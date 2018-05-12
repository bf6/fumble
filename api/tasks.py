import os
from bson.son import SON
from datetime import datetime, timedelta

from celery import Celery
from dateutil import parser

from db import MongoDB


celery = Celery('tasks', broker=os.environ['BROKER_URL'])


@celery.task
def task_get_matches(record):
    """
    For a given userId, set of coordinates, and datetime
    find all users that were nearby within 1 minute of
    user identified by userId
    """
    db = MongoDB().connect()
    # Hack b/c of Celery's serialization converting
    # datetimes to strings
    record['time'] = parser.parse(record['time'])

    locs = db.user_locations.find({
        'loc': {
            '$geoNear': {
                '$geometry': record['loc'],
                '$maxDistance': 150,
            },
        },
        'userId': {'$ne': record['userId']},
        'time': {
            '$gte': record['time'] - timedelta(seconds=30),
            '$lte': record['time'] + timedelta(seconds=30)
        },
    })

    for loc in locs:
        # For each match, create two records.
        criteria = {'from': record['userId'], 'to': loc['userId']}
        new_values = criteria.copy()
        new_values.update({'time': record['time']})
        # Update existing or create new record
        db.matches.update(criteria, new_values, upsert=True)
        # Symmetrical - both users get a match made `to` them `from` the other user
        reversed_criteria = {'from': loc['userId'], 'to': record['userId']}
        new_values.update(reversed_criteria)
        db.matches.update(reversed_criteria, new_values, upsert=True)
