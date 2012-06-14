from django.test import TestCase
from portcullis.models import DataStream, ScalingFunction, Device, DevicePermission, Key

class PermissionTest(TestCase):

    def setUp(self):
        scale = ScalingFunction(name = "identity", definition = "return x;").save()

        s1 = DataStream.objects.create(node_id = 0, port_id = 0, name = "stream 1", scaling_function = scale)
        s2 = DataStream.objects.create(node_id = 0, port_id = 1, name = "stream 2", scaling_function = scale)
        s3 = DataStream.objects.create(node_id = 0, port_id = 2, name = "stream 3", scaling_function = scale)

        k1 = Key.objects.create(key = "apple")
        k2 = Key.objects.create(key = "pear")
        k3 = Key.objects.create(key = "cherry")

        d1 = Device.objects.create(name = "device 1", key = k1)
        d2 = Device.objects.create(name = "device 2", key = k2)
        d3 = Device.objects.create(name = "device 3", key = k3)

        DevicePermission.objects.create(datastream = s1, device = d1, write = True)
        DevicePermission.objects.create(datastream = s2, device = d2, write = True)
        DevicePermission.objects.create(datastream = s3, device = d3, write = True)
        DevicePermission.objects.create(datastream = s1, device = d2)
        DevicePermission.objects.create(datastream = s1, device = d3, write = True)
        DevicePermission.objects.create(datastream = s2, device = d3, write = True)

        
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
        
