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
from graphs.models import DataStream, SensorReading, Sensor, ScalingFunction
from portcullis.models import PortcullisUser
from portcullis.customExceptions import SensorReadingCollision

from api.views.reading_loader import insert_reading
from api.views.sensor import claimSensor
from api.views.datastream import create as createDs


class HelperMethods(TestCase):
    '''
    '  Collection of methods to help in the testing process such as quick creation of dummy objects for the db.
    '''

    def createDummySensor(self):
        '''
            Helper to create a new dummy sensor
        '''

        ns = Sensor(uuid="foo")
        ns.save()
        return ns

    def createClaimedSensor(self):
        '''
            Helper to create a new dummy claimed sensor
        '''

        sensor = self.createDummySensor()
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        newCs = ClaimedSensor(sensor=sensor, owner=owner, name="foo_cs")
        newCs.save()
        return newCs


class ReadingLoaderTest(TestCase):
    '''
    ' Tests for the view file reading_loader.py
    '''
   
    fixtures = ['portcullisUsers.json', 'sensors.json', 'scalingFunctions.json',  'dataStreams.json']

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


class SensorTest(HelperMethods):
    '''
    '  Tests for the view file sensor.py
    '''

    fixtures = ['portcullisUsers.json', 'sensors.json', 'scalingFunctions.json',  'dataStreams.json']

    def setUp(self):
        self.c = Client()


    ################# claimSensor ################

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
        self.assertTrue(isinstance(cs, str))
   

    def test_claimSensor_update_sensor(self):
        '''
            Test that we get back the same ClaimedSensor we are updating the sensor on.
        '''

        name = "Claimed Sensor One"
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        newSensor = self.createDummySensor()
        
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
        newSensor = self.createDummySensor()
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


    
    ################# create ################

    def test_create_no_owner(self):
        '''
            Test that we get back the claimed sensor we give even when not giving an owner
        '''

        data = {"uuid": "sensor_one_id", "name": "Claimed Sensor One"} 
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        self.assertEqual(create(data, None), sensor)


    def test_create_no_uuid(self):
        '''
            Test that we get back an error should we not send a uuid 
        '''

        data = {"name": "Claimed Sensor One"} 
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        self.assertTrue(isinstance(create(data, owner), str))
    
    
    def test_create_no_name(self):
        '''
            Test that we get back the sensor we send when we don't give a name
        '''

        data = {"uuid": "sensor_one_id"} 
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        self.assertEqual(create(data, owner), sensor)


    def test_create_good_data_create(self):
        '''
            Test that we get back a new sensor given good data
        '''

        data = {"uuid": "brand_new_sensor", "name": "Brand New Name"} 
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        sensor = create(data, owner)
        self.assertTrue(isinstance(sensor, Sensor))
        self.assertEqual(Sensor.objects.get(uuid="brand_new_sensor"), sensor)


    def test_create_good_data_unclaimed_update(self):
        '''
            Test that we get back a updated sensor given good data and the sensor is not claimed
        '''

        newSensor = self.createDummySensor()
        data = {"uuid": newSensor.uuid, "name": "Claimed Sensor One", "units": "new units"} 
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        updatedSensor = create(data, owner)

        self.assertTrue(isinstance(updatedSensor, Sensor))
        self.assertNotEqual(updatedSensor.units, sensor.units)


    def test_create_swap_sensor(self):
        '''
            Test that we can claim a new sensor.
        '''

        data = {"uuid": "brand_new_sensor", "name": "Claimed Sensor One"} 
        owner = PortcullisUser.objects.get(email="admin@visgence.com")

        claimedSensor = ClaimedSensor.objects.get(owner=owner, name=data['name'])
        oldSensor = Sensor.objects.get(uuid="sensor_one_id")
        self.assertEqual(claimedSensor.sensor, oldSensor)

        newSensor = create(data, owner)
        self.assertTrue(isinstance(newSensor, Sensor)) 
        self.assertNotEqual(newSensor, oldSensor)
        self.assertEqual(ClaimedSensor.objects.get(sensor=newSensor), claimedSensor)


class DataStreamTest(HelperMethods):
    '''
    ' Tests for the view file datastream.py
    '''

    fixtures = ['portcullisUsers.json', 'sensors.json', 'claimedSensors.json', 'scalingFunctions.json',  'dataStreams.json']

    
    ################# claimDs ################
    
    def test_create_new_ds(self):
        '''
            Test that we create a ds and claim it to a given sensor that doesn't have a ds yet
        '''

        dummySensor = self.createDummySensor()
        self.assertRaises(DataStream.DoesNotExist, DataStream.objects.get, **{'sensor': dummySensor})
        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        data = {'name': 'foo_ds'}
        newDs = createDs(dummySensor, owner, data)
        
        self.assertTrue(isinstance(newDs, DataStream))
        try:
            ds = DataStream.objects.get(sensor=dummySensor)
        except DataStream.DoesNotExist:
            self.fail('No DataStream with Sensor \'%s\''%dummySensor)
        self.assertEqual(newDs, ds)


    def test_create_update_ds(self):
        '''
            Test that we update a ds given it's sensor that is has claimed and new data
        '''

        owner = PortcullisUser.objects.get(email="admin@visgence.com")
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        ds = DataStream.objects.get(sensor=sensor)
        newData = {
            'color': '#FFFFFF'
            ,'min_value': 1.1
            ,'max_value': 1.1
            ,'reduction_type': 'median'
            ,'is_public': False
            ,'scaling_function': ScalingFunction.objects.get(name="Kbps")
            ,'name': "new foo name"
            ,'description': 'blarg'
            ,'units': 'some units'
        }

        #First test that the new values don't already exist in the ds
        valueExists = False
        for field in ds._meta._fields():
            if field.name in newData and newData[field.name] == getattr(ds, field.name):
                valueExists = True

        self.assertFalse(valueExists)
        updatedDs = createDs(sensor, owner, newData)
        self.assertEquals(updatedDs, DataStream.objects.get(sensor=sensor)) 
        
        #Test values again on the updated ds to make sure they got updated
        valuesUpdated = True
        for field in updatedDs._meta._fields():
            if field.name in newData and newData[field.name] != getattr(updatedDs, field.name):
                valuesUpdated = False

        self.assertTrue(valuesUpdated)

    def test_create_invalid_credentials(self):
        '''
            Test that we get an error string when we try to update a DataStream with a claimed
            sensor but a different owner.
        '''

        owner = PortcullisUser.objects.get(email="normal@visgence.com")
        sensor = Sensor.objects.get(uuid="sensor_one_id")
        ds = DataStream.objects.get(sensor=sensor)
        self.assertNotEqual(ds.owner, owner)
        updatedDs = createDs(sensor, owner, {})
        self.assertEquals(updatedDs, "Invalid Credentials")
        
