"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
#System imports
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
#Local imports
from portcullis.models import DataStream
from data_loader import validate_stream


class addReadingTest(TestCase):
    
    def setUp(self):
        self.client = Client()

    def test_auth_token(self):
        response = self.client.get('/collector/add_reading/', {'auth_token':"IncorrectToken"})
        self.assertEqual(response.content, "Incorrect Authentication!")

class validateStreamTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('david', 'blah@weiner.com', 'hunter1')
        self.stream = DataStream.objects.create(id=4, node_id=1, port_id=2, owner=self.user)

    def test_stream_id_validation(self):
        """
        Tests that validation works for stream id
        """

        info = validate_stream(4, None, None)
        self.assertEqual(info['datastream'], self.stream)

    def test_stream_node_port_validation(self):
        """
        Tests that validation works for node/port combo's
        """

        info = validate_stream(None, 1, 2)
        self.assertEqual(info['datastream'], self.stream)

    def test_node_validation(self):
        """
        Tests that validation fails for only a node_id
        """

        info = validate_stream(None, 1, None)
        self.assertEqual(info['error'], "Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.\"\n\n")

    def test_port_validation(self):
        """
        Tests that validation fails for only a port_id
        """

        info = validate_stream(None, None, 2)
        self.assertEqual(info['error'], "Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.\"\n\n")
