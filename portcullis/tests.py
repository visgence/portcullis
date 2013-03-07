from django.test import TestCase
from portcullis.models import Key, PortcullisUser, DataStream, Device, ScalingFunction
from django.contrib.auth.models import User


class ScalingFunctionsTest(TestCase):
    '''
    ' Unit Tests for the portcullis model ScalingFunctions
    '''

    fixtures = ['portcullisUsers.json', 'scalingFunctions.json']

    def test_get_editable_scalingFunctions_by_user(self):
        '''
        ' Test that a user get's all scalingFunctions using getEditable from PortcullisUsers
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        scalingFunctions = ScalingFunction.objects.all()

        scalingFuns = ScalingFunction.objects.getEditable(user)
        self.assertEqual(list(scalingFunctions), list(scalingFuns))
    
    def test_get_editable_scalingFunctions_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using PortcullisUser's getEditable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, PortcullisUser.objects.getEditable, user=aUser)


class PortcullisUserTest(TestCase):
    '''
    ' Unit Tests for the portcullis model PortcullisUser
    '''

    fixtures = ['portcullisUsers.json']

    def test_get_editable_users_by_superuser(self):
        '''
        ' Test that a superuser get's all users using getEditable from PortcullisUsers
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        users = PortcullisUser.objects.all()

        sPortcullisUsers = PortcullisUser.objects.getEditable(sUser)
        self.assertEqual(list(sPortcullisUsers), list(users))
    
    def test_get_editable_users_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her users using getEditable from PortcullisUsers
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")

        nPortcullisUsers = PortcullisUser.objects.getEditable(nUser)
        self.assertEqual([nUser], list(nPortcullisUsers))

    def test_get_editable_users_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using PortcullisUser's getEditable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, PortcullisUser.objects.getEditable, user=aUser)


class KeyTest(TestCase):
    '''
    ' Unit Tests for the portcullis model Key
    '''

    fixtures = ['portcullisUsers.json', 'keys.json']

    def test_get_editable_keys_by_superuser(self):
        '''
        ' Test that a superuser get's all keys using getEditable from Keys
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        keys = Key.objects.all()

        sKeys = Key.objects.getEditable(sUser)
        self.assertEqual(list(sKeys), list(keys))
    
    def test_get_editable_keys_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her keys using getEditable from Keys
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        keys = Key.objects.filter(owner = nUser)

        nKeys = Key.objects.getEditable(nUser)
        self.assertEqual(list(keys), list(nKeys))

    def test_get_editable_keys_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using Key's getEditable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, Key.objects.getEditable, user=aUser)

class DeviceTest(TestCase):
    '''
    ' Unit Tests for the portcullis model Device
    '''

    fixtures = ['portcullisUsers.json', 'devices.json']

    def test_get_editable_devices_by_superuser(self):
        '''
        ' Test that a superuser get's all devices using getEditable from Devices
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        devices = Device.objects.all()

        sDevices = Device.objects.getEditable(sUser)
        self.assertEqual(list(sDevices), list(devices))
    
    def test_get_editable_devices_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her devices using getEditable from Devices
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        devices = Device.objects.filter(owner = nUser)

        nDevices = Device.objects.getEditable(nUser)
        self.assertEqual(list(devices), list(nDevices))

    def test_get_editable_devices_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using Device's getEditable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, Device.objects.getEditable, user=aUser)


class DataStreamTest(TestCase):
    '''
    ' Unit Tests for the portcullis model DataStream
    '''

    fixtures = ['portcullisUsers.json', 'scalingFunctions.json', 'datastreams.json']

    def test_get_editable_datastreams_by_superuser(self):
        '''
        ' Test that a superuser get's all datastreams using getEditable from DataStreams
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        datastreams = DataStream.objects.all()

        sDataStreams = DataStream.objects.getEditable(sUser)
        self.assertEqual(list(sDataStreams), list(datastreams))
    
    def test_get_editable_datastreams_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her datastreams using getEditable from DataStreams
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        datastreams = DataStream.objects.filter(owner = nUser)

        nDataStreams = DataStream.objects.getEditable(nUser)
        self.assertEqual(list(datastreams), list(nDataStreams))

    def test_get_editable_datastreams_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using DataStream's getEditable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, DataStream.objects.getEditable, user=aUser)



"""
class PermissionTest(TestCase):
    fixtures = ['portcullis.xml']

    def test_device_by_key(self):
        '''Can we get a device by a key'''

        myKey = Key.objects.validate("apple")
        self.assertEqual(myKey.key, "apple")

        myBadKey = Key.objects.validate("foo")
        self.assertEqual(myBadKey, None)

        myDevice = Device.objects.get_by_key(myKey)
        self.assertEqual(myDevice.name, "device 1")

    def test_get_writable_by_device(self):
        '''Get all streams that are writable by a given device'''

        myDevice = Device.objects.get(name = "device 2")
        dataStreams = DataStream.objects.get_writable_by_device(myDevice).order_by('name')
        self.assertEqual(dataStreams[0].name, "stream 2")

        myDevice = Device.objects.get(name = "device 3")
        dataStreams = DataStream.objects.get_writable_by_device(myDevice).order_by('name')
        self.assertEqual(len(dataStreams), 3)
        self.assertEqual(dataStreams[0].name, "stream 1")
        self.assertEqual(dataStreams[1].name, "stream 2")
        self.assertEqual(dataStreams[2].name, "stream 3")

    def test_get_writable_by_key(self):
        '''Get all streams that are writable by a given key'''

        myKey = Key.objects.validate('pear')
        dataStreams = DataStream.objects.get_writable_by_key(myKey)
        self.assertEquals(dataStreams[0].name, "stream 2")
"""
