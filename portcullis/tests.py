
#System Imports
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime

#Local Imports
from portcullis.models import Key, PortcullisUser, DataStream, Device, ScalingFunction


class ScalingFunctionsTest(TestCase):
    '''
    ' Unit Tests for the portcullis model ScalingFunctions
    '''

    fixtures = ['portcullisUsers.json', 'scalingFunctions.json']

    def test_get_editable_scalingFunctions_by_user(self):
        '''
        ' Test that a user get's all scalingFunctions using get_editable from PortcullisUsers
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        scalingFunctions = ScalingFunction.objects.all()

        scalingFuns = ScalingFunction.objects.get_editable(user)
        self.assertEqual(list(scalingFunctions), list(scalingFuns))
    
    def test_get_editable_scalingFunctions_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using PortcullisUser's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, PortcullisUser.objects.get_editable, user=aUser)

class PortcullisUserTest(TestCase):
    '''
    ' Unit Tests for the portcullis model PortcullisUser
    '''

    fixtures = ['portcullisUsers.json']

    def test_get_editable_users_by_superuser(self):
        '''
        ' Test that a superuser get's all users using get_editable from PortcullisUsers
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        users = PortcullisUser.objects.all()

        sPortcullisUsers = PortcullisUser.objects.get_editable(sUser)
        self.assertEqual(list(sPortcullisUsers), list(users))
    
    def test_get_editable_users_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her users using get_editable from PortcullisUsers
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")

        nPortcullisUsers = PortcullisUser.objects.get_editable(nUser)
        self.assertEqual([nUser], list(nPortcullisUsers))

    def test_get_editable_users_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using PortcullisUser's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, PortcullisUser.objects.get_editable, user=aUser)

class KeyTest(TestCase):
    '''
    ' Unit Tests for the portcullis model Key
    '''

    fixtures = ['portcullisUsers.json', 'keys.json']

    def test_get_editable_keys_by_superuser(self):
        '''
        ' Test that a superuser get's all keys using get_editable from Keys
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        keys = Key.objects.all()

        sKeys = Key.objects.get_editable(sUser)
        self.assertEqual(list(sKeys), list(keys))
    
    def test_get_editable_keys_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her keys using get_editable from Keys
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        keys = Key.objects.filter(owner = nUser)

        nKeys = Key.objects.get_editable(nUser)
        self.assertEqual(list(keys), list(nKeys))

    def test_get_editable_keys_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using Key's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, Key.objects.get_editable, user=aUser)
    
    def test_isCurrent_expired_key(self):
        '''
        ' Test that an expired key get's false returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "exp_key")
        self.assertFalse(key.isCurrent())

    def test_isCurrent_no_uses_key(self):
        '''
        ' Test that a key with no uses get's false returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "no_uses_key")
        self.assertFalse(key.isCurrent())

    def test_isCurrent_has_uses_key(self):
        '''
        ' Test that a key with uses left get's true returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "valid_uses_key")
        self.assertTrue(key.isCurrent())

    def test_isCurrent_valid_exp_key(self):
        '''
        ' Test that a key with a non expired date get's true returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "valid_date_key")
        self.assertTrue(key.isCurrent())

    def test_isCurrent_valid_key(self):
        '''
        ' Test that a key with both valid date and num uses get's true returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "valid_key")
        self.assertTrue(key.isCurrent())

    def test_validate_bad_token(self):
        '''
        ' Test that KeyManager validate returns None if a bad token is supplied.
        '''

        badToken = "HADUUUUKIN!!"
        self.assertEquals(Key.objects.validate(badToken), None)

    def test_validate_exp_date(self):
        '''
        ' Test that KeyManager validate returns None if an expired date token is supplied.
        '''

        expToken = Key.objects.get(key = "exp_key")
        self.assertEquals(Key.objects.validate(expToken.key), None)

    def test_validate_no_uses(self):
        '''
        ' Test that KeyManager validate returns None if a token with no uses is supplied.
        '''

        expToken = Key.objects.get(key = "no_uses_key")
        self.assertEquals(Key.objects.validate(expToken.key), None)
    
    def test_validate_valid_uses(self):
        '''
        ' Test that KeyManager validate returns the key supplied if the supplied key has uses left. 
        '''

        key = Key.objects.get(key = "valid_uses_key")
        self.assertEquals(Key.objects.validate(key.key), key)

class DeviceTest(TestCase):
    '''
    ' Unit Tests for the portcullis model Device
    '''

    fixtures = ['portcullisUsers.json', 'devices.json']

    def test_get_editable_devices_by_superuser(self):
        '''
        ' Test that a superuser get's all devices using get_editable from Devices
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        devices = Device.objects.all()

        sDevices = Device.objects.get_editable(sUser)
        self.assertEqual(list(sDevices), list(devices))
    
    def test_get_editable_devices_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her devices using get_editable from Devices
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        devices = Device.objects.filter(owner = nUser)

        nDevices = Device.objects.get_editable(nUser)
        self.assertEqual(list(devices), list(nDevices))

    def test_get_editable_devices_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using Device's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, Device.objects.get_editable, user=aUser)

class DataStreamTest(TestCase):
    '''
    ' Unit Tests for the portcullis model DataStream
    '''

    fixtures = ['portcullisUsers.json', 'keys.json', 'scalingFunctions.json', 'datastreams.json']

    def test_get_editable_datastreams_by_superuser(self):
        '''
        ' Test that a superuser get's all datastreams using get_editable from DataStreams
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        datastreams = DataStream.objects.all()

        sDataStreams = DataStream.objects.get_editable(sUser)
        self.assertEqual(list(sDataStreams), list(datastreams))
    
    def test_get_editable_datastreams_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her datastreams using get_editable from DataStreams
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        datastreams = DataStream.objects.filter(owner = nUser)

        nDataStreams = DataStream.objects.get_editable(nUser)
        self.assertEqual(list(datastreams), list(nDataStreams))

    def test_get_editable_datastreams_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using DataStream's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, DataStream.objects.get_editable, user=aUser)

    def test_get_readable_by_non_key(self):
        '''
        ' Test that a non Key object raises an exception when using DataStream's get_readable_by_key
        '''
        
        nonKey = "I am a Key... NOT!!!!"
        self.assertRaises(TypeError, DataStream.objects.get_readable_by_key, key=nonKey)

    def test_get_readable_by_date_expired_key(self):
        '''
        ' Test that a Key which has an expired date raises an exception when using DataStream's get_readable_by_key
        '''
        
        expKey = Key.objects.get(key="exp_key")
        try:
            DataStream.objects.get_readable_by_key(expKey)
        except Exception as e:
            self.assertEqual(str(e), "None is not a valid key.")

    def test_get_readable_by_no_uses_key(self):
        '''
        ' Test that a Key which has no more uses raises an exception when using DataStream's get_readable_by_key
        '''

        noUsesKey = Key.objects.get(key="no_uses_key")
        try:
            DataStream.objects.get_readable_by_key(noUsesKey)
        except Exception as e:
            self.assertEqual(str(e), "None is not a valid key.")

    def test_get_readable_by_valid_key(self):
        '''
        ' Test that a Key which is valid returns a QuerySet of appropriate DataStreams when using DataStream's 
        ' get_readable_by_key
        '''

        validKey = Key.objects.get(key="valid_key")
        dStream = DataStream.objects.filter(can_read = validKey)

        self.assertEqual(list(dStream), list(DataStream.objects.get_readable_by_key(validKey)))

    def test_get_readable_by_valid_date_key(self):
        '''
        ' Test that a Key which is valid by it's date returns a QuerySet of appropriate DataStreams when using DataStream's 
        ' get_readable_by_key
        '''

        validKey = Key.objects.get(key="valid_date_key")
        dStream = DataStream.objects.filter(can_read = validKey)

        self.assertEqual(list(dStream), list(DataStream.objects.get_readable_by_key(validKey)))

    def test_get_readable_by_valid_uses_key(self):
        '''
        ' Test that a Key which is valid by it's num_uses returns a QuerySet of appropriate DataStreams when using DataStream's 
        ' get_readable_by_key
        '''

        validKey = Key.objects.get(key="valid_uses_key")
        dStream = DataStream.objects.filter(can_read = validKey)

        self.assertEqual(list(dStream), list(DataStream.objects.get_readable_by_key(validKey))) 

    def test_get_viewable_by_user_non_user(self):
        '''
        ' Test that a non PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' throws a TypeError
        '''

        nonUser = "I are a PortcullisUser huehuehue"
        self.assertRaises(TypeError, DataStream.objects.get_viewable_by_user, user = nonUser)

    def test_get_viewable_by_user_super_user(self):
        '''
        ' Test that a super PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' gets all DataStreams that he doesn't own.
        '''
    
        sUser = PortcullisUser.objects.get(username="superuser")
        sStreams = DataStream.objects.all()

        vStreams = DataStream.objects.get_viewable_by_user(sUser)
        self.assertEqual(list(sStreams), list(vStreams))

    def test_get_viewable_by_user_non_valid_keys(self):
        '''
        ' Test that a normal PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' gets no DataStreams that he has keys for but those keys are all invalid (expired or no more uses)
        '''

        user = PortcullisUser.objects.get(username="invalidkeysuser")
        uStreams = DataStream.objects.get_viewable_by_user(user)
        self.assertEqual(list(uStreams), [])

    def test_get_viewable_by_user_valid_keys(self):
        '''
        ' Test that a normal PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' gets DataStreams that he has valid keys for
        '''

        user = PortcullisUser.objects.get(username="validkeysuser")
        d1 = DataStream.objects.get(pk = 3)
        d2 = DataStream.objects.get(pk = 4)
        d3 = DataStream.objects.get(pk = 5)
        d4 = DataStream.objects.get(pk = 6)
        dStreams = [d1, d2, d3, d4]

        uStreams = DataStream.objects.get_viewable_by_user(user)
        self.assertEqual(list(uStreams), dStreams)
