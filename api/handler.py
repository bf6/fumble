from bson import json_util as json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from db import MongoDB
from tasks import task_get_matches


class FumbleHandler(BaseHTTPRequestHandler):
    _connection = None
    # Dict of valid POST fields and types
    valid_post = {
        'userId': int,
        'lat': float,
        'lng': float,
        'time': int,
    }

    @property
    def db(self):
        if self._connection is None:
            self._connection = MongoDB().connect()
        return self._connection

    def _read_post(self):
        """
        Read the body of the POST return it as a dict
        """
        length = int(self.headers.get('Content-Length', 0))
        field_data = self.rfile.read(length)
        return json.loads(field_data) if field_data else None

    def _send_response(self, status_code, message):
        """
        Return a status code and response message
        """
        self.send_response(status_code)
        self.end_headers()
        self.wfile.write(json.dumps({"message": message}).encode())

    def do_POST(self):
        """
        Validate POST data or return error message
        Store user_location and return 202 ACCEPTED
        """
        # Read body of POST request
        data = self._read_post()
        # Return error if empty/missing body
        if not data:
            self._send_response(400, "Could not parse body")
            return
        # Validate POST body has required fields and types
        for field, type_ in self.valid_post.items():
            if field not in data:
                self._send_response(400, "Missing required field: {}".format(field))
                return
            elif not isinstance(data[field], type_):
                self._send_response(400, "{} should be a {}".format(field, type_.__name__))
                return

        # We're going to upsert - so search by `criteria` and update with `new_values`
        criteria = {'userId': data['userId']}
        new_values = criteria.copy()
        new_values.update({
            'loc': {'type': 'Point', 'coordinates': [data['lng'], data['lat']]},
            'time': datetime.utcfromtimestamp(data['time']),
        })

        # Write to Mongo
        self.db.user_locations.update(criteria, new_values, upsert=True)

        # Task to create matches
        task_get_matches.delay(new_values)
        #task_get_matches(new_values)

        # Respond with 202 Accepted
        self._send_response(202, 'Accepted!')
        return


    def do_GET(self):
        """
        Return all matches for a given user identified by userId
        """
        # Parse userID from queryparams
        user_id = parse_qs(urlparse(self.path).query).get('userId')
        # If userId is missing, error response
        if not user_id:
            self._send_response(400, 'Missing userId parameter')

        # Find all matches sent 'to' the user
        user_id = int(user_id[0])
        matches = list(self.db.matches.find({'to': user_id}, {'_id': 0}))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({'items': matches}).encode())
        return
