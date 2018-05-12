import mock
from http import server
from io import BytesIO as IO
from unittest import TestCase

from handler import FumbleHandler


mock_request = mock.Mock()


class MockServer(object):
    def __init__(self, ip_port, Handler):
        handler = Handler(mock_request, ip_port, self)


class TestHandler(TestCase):
    # TODO: Write tests

    @classmethod
    def setUpClass(cls):
        """ Set up the mock server
            to handle the request
        cls.server = MockServer(('0.0.0.0', 8000), FumbleHandler)
        """

    def test_get_success(self):
        """
        Test we can get a record we know exists
        """

    def test_get_failure(self):
        """
        Test we can't GET with missing query params
        """

    def test_post_success(self):
        """
        Test we can POST
        """

    def test_post_failure(self):
        """
        Test we get a 400 for known failure conditions
        """

    def test_match_created(self):
        """
        Create two user_locations close enough to match
        and assert they do - we should get match back
        for each of them when we GET 
        """

    def test_match_not_created(self):
        """
        Create two user_location records not close
        enough to be a match (either time or distance or
        both) and validate that no match is created
        """
