"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
#System imports
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
import time

#Local imports
from portcullis.models import DataStream, SensorReading, UserPermission


class renderGraphTest(TestCase):
    
    def setUp(self):
        self.client = Client()

        myStream = DataStream.objects.create(node_id = 0, port_id = 0)

        for i in range(100000):
            SensorReading.objects.create(datastream = myStream, timestamp = 1339789049 + i, value = 32)

        user = User.objects.create_user('fakename', 'fake@pukkared.com', 'mypassword')
        UserPermission.objects.create(datastream = myStream, user = user, owner = False)

    '''
    def test_no_permission(self):
 
        #use test client to perform login
        user_login = self.client.login(username='fakename', password='mypassword')


        response = self.client.get('/render_graph/?json=true&start=1339780000&end=1339789269&granularity=300&datastream_id=1')
        self.assertEqual(response.content, "Incorrect Authentication!")
    '''

    def test_data_time(self):
        t1 = time.time()
        readings = SensorReading.objects.all()
        t2 = time.time()

        print "Time for grabbing all sensor readings: %f" % (t2 - t1)

        self.assertEqual(1+1, 2)
