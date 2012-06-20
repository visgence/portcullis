from django.test import TestCase
from django.contrib.auth.models import User
from portcullis.models import DataStream, ScalingFunction, Device, DevicePermission, Key

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
        
