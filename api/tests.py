""""
" api/tests.py
"
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2013 Visgence, Inc.
"""

#Django Imports
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
AuthUser = get_user_model()

#System Imports
#from urllib import urlencode, urlopen
import time
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from graphs.models import DataStream, SensorReading, Sensor, ClaimedSensor
from portcullis.models import PortcullisUser
from portcullis.customExceptions import SensorReadingCollision
from api.views.reading_loader import insert_reading
from api.views.sensor import claimSensor


class CreateTest(TestCase):
    '''
    ' Tests for the view file create.py
    '''

    fixtures = ['test_keys.json', 'test_scalingFunctions.json', 'test_portcullisUsers.json', 'test_dataStreams.json']

    def setUp(self):
        self.json_data = {
            'name': "new stream",
            'scaling_function': "Identity", 
            'reduction_type': "mean",
            'is_public': True,
        }

        self.c = Client()

    def get_json(self, token):
        '''
        ' Helper method for tests that prep's the json data for createDs
        '''

        data = {
            'token': token,
            'ds_data': self.json_data
        }
        return json.dumps(data)



    ################### createDs ###################
    
    def test_createDs_keyDoesNotExist(self):
        '''
        ' If given a key token that does not exist we should get back json with a specific
        ' error message.
        '''

        json_data = self.get_json("bad token")
        response = self.c.post('/api/create_ds/', {'jsonData':json_data})
        response_json = json.loads(response.content)
        self.assertEquals(response_json['error'], "From createDs: Key with token 'bad token' does not exist.")
      
    def test_createDs_badJsonKey(self):
        '''
        ' If the post request can't find jsonData then we should get back json with a specific error.
        '''

        json_data = self.get_json("bad token")
        response = self.c.post('/api/create_ds/', {'bad_key':json_data})
        response_json = json.loads(response.content)
        self.assertEqual(response_json['error'], "From createDs: Problem getting json data from request.")

    def test_createDs_streamExists(self):
        '''
        ' We should get back the id of a existant datastream if we try to create one with the same owner and name.
        '''

        ds = DataStream.objects.get(pk=1, name="superuser_ds1")
        self.json_data['name'] = ds.name
        json_data = self.get_json("superuser_key1")
        response = self.c.post('/api/create_ds/', {'jsonData':json_data})
        response_json = json.loads(response.content)
        same_ds = DataStream.objects.get(pk=response_json['id'])
        
        self.assertEquals(same_ds, ds)
        
    def test_createDs_newStream(self):
        '''
        ' We should get the id of a newly created DataStream if we give a proper json information.
        '''

        #First make sure the ds does not exist yet.
        owner = AuthUser.objects.get(pk=1)
        self.assertRaises(DataStream.DoesNotExist, DataStream.objects.get, owner=owner, name=self.json_data['name'])
        json_data = self.get_json("superuser_key1")
        response = self.c.post('/api/create_ds/', {'jsonData': json_data})
        response_json = json.loads(response.content)
        new_ds = DataStream.objects.get(pk=response_json['id'])        
        self.assertEqual(new_ds, DataStream.objects.get(owner=owner, name=self.json_data['name']))

    def test_createDs_badScalingFunction(self):
        '''
        ' If we give a bad scaling function name in the json data we should get back a specific
        ' error message
        '''
       
        self.json_data['scaling_function'] = "bad sc name"
        json_data = self.get_json("superuser_key1")
        response = self.c.post('/api/create_ds/', {'jsonData':json_data})
        response_json = json.loads(response.content)
        
        self.assertEqual(response_json['error'], "From createDs: scaling function with name 'bad sc name' does not exist.")
    
    def test_createDs_badNameAttr(self):
        '''
        ' If we give an attribute for a new datastream that is not right, in this case setting owner to and None, we should
        ' get an error back.
        '''

        self.json_data['reduction_type'] = "bad choice" 
        json_data = self.get_json("superuser_key1")
        response = self.c.post('/api/create_ds/', {'jsonData':json_data})
        response_json = json.loads(response.content)
        
        self.assertEqual(response_json['error'], "From createDs: There were one or more problems setting DataStream attributes.")


class ReadingLoaderTest(TestCase):
    '''
    ' Tests for the view file reading_loader.py
    '''
   
    fixtures = ['portcullisUsers.json', 'sensors.json', 'claimedSensors.json', 'scalingFunctions.json',  'dataStreams.json']

    def setUp(self):
        self.c = Client()


    ################# insert_reading ################

    def test_insert_reading_no_ds(self):
        '''
            Test that we get a new sensor reading even with no datastream
        '''

        sensor = Sensor.objects.get(uuid="sensor_one_id")
        timestamp = int(time.time())
        reading = insert_reading(None, sensor, 10.5, timestamp) 
        self.assertEqual(reading, SensorReading.objects.get(datastream=None, timestamp=timestamp))

    def test_insert_reading_ds(self):
        '''
            Test that we get a new sensor reading with a datastream
        '''
        
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        ds = DataStream.objects.get(pk=1)
        timestamp = int(time.time())
        reading = insert_reading(ds, sensor, 10.5, timestamp) 
        self.assertEqual(reading, SensorReading.objects.get(datastream=ds, timestamp=timestamp))

    def test_insert_reading_no_timestamp(self):
        '''
            Test that a sensor reading get's creating without an explicit timestamp
        '''
        
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        ds = DataStream.objects.get(pk=1)
        reading = insert_reading(ds, sensor, 10.5) 
        self.assertTrue(isinstance(reading, SensorReading))

    def test_insert_reading_collision(self):
        '''
            Test that if we insert two readings with the same timestamp and datastream we get a collision
        '''
        
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        ds = DataStream.objects.get(pk=1)
        timestamp = int(time.time())
        insert_reading(ds, sensor, 10.5, timestamp) 
        self.assertRaises(SensorReadingCollision, insert_reading, *(ds, sensor, 10.5, timestamp) )


class SensorTest(TestCase):
    '''
    '  Tests for the view file sensor.py
    '''

    fixtures = ['portcullisUsers.json', 'sensors.json', 'claimedSensors.json', 'scalingFunctions.json',  'dataStreams.json']

    def setUp(self):
        self.c = Client()

    def createSensor(self):
        '''
            Helper to create a new dummy sensor
        '''

        ns = Sensor(uuid="foo")
        ns.save()
        return ns


    def test_claimSensor_no_sensor(self):
        '''
            Test that we get an error message if given no sensor instance
        '''

        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        name = "Claimed Sensor One"
        cs = claimSensor(None, name, owner)
        self.assertTrue(isinstance(cs, list))


    def test_claimSensor_no_name(self):
        '''
            Test that we get an error message if given no name
        '''

        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        cs = claimSensor(sensor, None, owner)
        self.assertTrue(isinstance(cs, list))


    def test_claimSensor_no_owner(self):
        '''
            Test that we get an error message if given no owner
        '''

        sensor = Sensor.objects.get(uuid="sensor_one_id")
        name = "Claimed Sensor One"
        cs = claimSensor(sensor, name, None)
        self.assertTrue(isinstance(cs, list))
    
    def test_claimSensor_update_sensor(self):
        '''
            Test that we get back the same ClaimedSensor we are updating the sensor on.
        '''

        name = "Claimed Sensor One"
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        newSensor = self.createSensor()
        
        csOne = ClaimedSensor.objects.get(owner=owner, name=name)
        csTwo = claimSensor(newSensor, name, owner)
        self.assertTrue(isinstance(csTwo, ClaimedSensor))
        self.assertEqual(csOne.pk, csTwo.pk)
        self.assertNotEqual(csOne.sensor, csTwo.sensor)

    def test_claimSensor_create(self):
        '''
            Test that a new claimed sensor get's created when given owner/name combo that does exist yet.
        '''

        name = "New Sensor Name"
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        newSensor = self.createSensor()
        self.assertRaises(ClaimedSensor.DoesNotExist, ClaimedSensor.objects.get, **{'name': name, 'owner': owner})

        cs = claimSensor(newSensor, name, owner)
        newCs = None
        try:
            newCs = ClaimedSensor.objects.get(owner=owner, name=name)
        except ClaimedSensor.DoesNotExist:
            pass

        self.assertNotEqual(newCs, None)
        self.assertTrue(isinstance(cs, ClaimedSensor))
        self.assertEqual(cs.pk, newCs.pk)

    def test_claimSensor_unique_sensor_violation(self):
        '''
            Test that a error occurs when creating a new ClaimedSensor with a sensor that is already claimed elsewhere.
        '''

        name = "New Sensor Name"
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        cs = claimSensor(sensor, name, owner)
        self.assertTrue(isinstance(cs, list))
        self.assertRaises(ClaimedSensor.DoesNotExist, ClaimedSensor.objects.get, **{'name': name, 'owner': owner})


