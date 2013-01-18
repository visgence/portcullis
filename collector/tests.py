"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
#System imports
from django.test import TestCase
from django.test.client import Client

#Local imports
from portcullis.models import DataStream, Key, Device, PortcullisUser
from data_loader import validate_stream


class addReadingTest(TestCase):
    
    def setUp(self):
        self.client = Client()

        owner = PortcullisUser.objects.create(username = "portcullis")
        myKey1 = Key.objects.create(key = "pear", owner = owner)
        myKey2 = Key.objects.create(key = "apple", owner = owner)

    def test_auth_token(self):
        response = self.client.get('/collector/add_reading/', {'auth_token':"cherry"})
        self.assertEqual(response.content, "Incorrect Authentication!")


    def test_raw_sensor_value(self):
        response = self.client.get('/collector/add_reading/', {'auth_token':"pear"})
        self.assertEqual(response.content, "No data was passed for insertion! Please be sure to pass some data. Example: value=233")

        response = self.client.get('/collector/add_reading/', {'auth_token':"pear", 'value':""})
        self.assertEqual(response.content, "No data was passed for insertion! Please be sure to pass some data. Example: value=233")


    def test_sensor_identifier(self):
        '''When no stream id and port/node id pair is given'''

        response = self.client.get('/collector/add_reading/', {'auth_token':"apple", 'value':200})
        self.assertEqual(response.content, "Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.")

        response = self.client.get('/collector/add_reading/', {'auth_token':"apple", 'value':200, 'datastream_id':""})
        self.assertEqual(response.content, "Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.")


class validateStreamTest(TestCase):

    def setUp(self):
        self.stream = DataStream.objects.create(id=4, node_id=1, port_id=2)

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

        info = validate_stream(None, 1, '')
        self.assertEqual(info['error'], "Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.\"\n\n")

    def test_port_validation(self):
        """
        Tests that validation fails for only a port_id
        """

        info = validate_stream(None, None, 2)
        self.assertEqual(info['error'], "Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.\"\n\n")

        info = validate_stream(None, '', 2)
        self.assertEqual(info['error'], "Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.\"\n\n")

class addReadingBulkTest(TestCase):
    
    def setUp(self):
        self.client = Client()

        owner = PortcullisUser.objects.create(username = "portcullis") 
        myKey1 = Key.objects.create(key = "pear", owner = owner)
        myKey2 = Key.objects.create(key = "apple", owner = owner)
        myDataStream = DataStream.objects.create(node_id = 1, port_id = 1)

    def test_auth_token(self):
        response = self.client.get('/collector/add_reading_bulk/', {'auth_token':"cherry",'json':'[[]]'})
        self.assertEqual(response.content, "Incorrect Authentication!")

    def test_json(self):
        response = self.client.get('/collector/add_reading_bulk/', {'auth_token':"pear"})
        self.assertEqual(response.content, "No json received. Please send a serialized array of arrays in the form [[node_id1,port_id1,value1],[node_id2,port_id2,value2]]")
    
    def test_single_insert(self):
        response = self.client.get('/collector/add_reading_bulk/', {'auth_token':'pear','json':'[[1,1,333]]'})
        self.assertEqual(response.content,'\n\nTotal Insertion Attempts: 1\n\nSuccessful Insertions : 1\n\nAll records inserted!') 
    
    def test_multiple_insert(self):
        response = self.client.get('/collector/add_reading_bulk/', {'auth_token':'pear','json':'[[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1,333],[1,1],[132,1,333],[1,333],[1,0,333]]'})
        self.assertEqual(response.content,'\nNo data was passed for insertion! Please be sure to pass some data.\n\nNode id 132 and port id 1 does not map to an existing datastream id.\n\nNo data was passed for insertion! Please be sure to pass some data.\n\nNode id 1 and port id 0 does not map to an existing datastream id.\n\n\nTotal Insertion Attempts: 45\n\nSuccessful Insertions : 41\n\nFailed Insertions : 4')
 


