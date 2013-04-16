""""
" datastreams/tests.py
"
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2013 Visgence, Inc.
"""

#System Imports
from django.test import TestCase
from django.test.client import Client
from urllib import urlencode, urlopen
from django.contrib.auth import get_user_model
AuthUser = get_user_model()
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from portcullis.models import DataStream

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


