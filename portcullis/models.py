from django.db import models
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ObjectDoesNotExist

class ScalingFunction(models.Model):
    id = models.AutoField(primary_key=True, db_column='function_id')
    name = models.CharField(max_length=32, unique=True, blank=True)
    definition = models.CharField(max_length=1000, blank=True)

    class Meta:
        db_table = u'scaling_functions'
    def __unicode__(self):
        return "Name: " + self.name + ", ID: %s," % self.id + " Definition: %s" % self.definition 

class KeyManager(models.Manager):
    def validate(self, key):
        try:
            return Key.objects.get(key = key)
        except ObjectDoesNotExist:
            return None

class Key(models.Model):
    key = models.CharField(primary_key=True, max_length=64)
    description = models.TextField(null = True, blank = True)
    objects = KeyManager()

    class Meta:
        db_table = u'key'

    def __unicode__(self):
        return self.key 


class DeviceManager(models.Manager):
    def get_by_key(self, key):
        return Device.objects.get(key = key)

class Device(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null = True, blank = True)
    ip_address = models.IPAddressField(null = True, blank = True)
    key = models.OneToOneField(Key, null = True, blank = True)
    objects = DeviceManager()

    class Meta:
        db_table = u'device'

    def __unicode__(self):
        return self.name


class DataStreamManager(models.Manager):
    
    def get_writable_by_device(self, device):
        return DataStream.objects.filter(devicepermission__device = device, devicepermission__write = True)

    def get_writable_by_key(self, key):
        device = Device.objects.get_by_key(key)
        return DataStream.objects.filter(devicepermission__device = device, devicepermission__write = True)

class DataStream(models.Model):
    id = models.AutoField(primary_key=True, db_column='datastream_id')
    node_id = models.IntegerField(null=True, blank=True)
    port_id = models.IntegerField(null=True, blank=True)
    units = models.CharField(max_length=32, null = True, blank=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64, null = True, blank=True)
    color = models.CharField(max_length=32, null = True, blank=True)
    min_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    max_value = models.DecimalField(null=True, max_digits=20,decimal_places=6, blank=True)
    scaling_function = models.ForeignKey(ScalingFunction, null=True, db_column='scaling_function', blank=True)
    reduction_type = models.CharField(max_length=32, null = True, blank=True)
    is_public = models.BooleanField()
    users = models.ManyToManyField(User, through='UserPermission')
    devices = models.ManyToManyField(Device, through='DevicePermission')
    objects = DataStreamManager()


    class Meta:
        db_table = u'data_streams'
        ordering = ['node_id', 'port_id', 'id']

    def __unicode__(self):
        return "Stream_ID: %s" % self.id  + " Node: %s," % self.node_id + " Port: %s," % self.port_id + " Name: " + self.name

class SensorReading(models.Model):
    id = models.AutoField(primary_key=True, db_column='read_id', editable=False)
    datastream = models.ForeignKey(DataStream)
    sensor_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    date_entered = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'sensor_reading'

    def __unicode__(self):
        return self.datastream.name + ", Value: %s," % self.sensor_value + " Date Entered: %s" % self.date_entered

class Permission(models.Model):
    read = models.BooleanField(default = True)
    write = models.BooleanField(default = False)

    class Meta:
        abstract = True
    
class DevicePermission(Permission):
    datastream = models.ForeignKey(DataStream)
    device = models.ForeignKey(Device)

    class Meta:
        db_table = u'device_permission'

    def __unicode__(self):
        return "Device: %s" % self.device.name + ", Datastream: %s," % self.datastream.name + " Read: %s" % self.read + ", Write: %s" % self.write

class UserPermission(Permission):
    datastream = models.ForeignKey(DataStream)
    user = models.ForeignKey(User)
    owner = models.BooleanField(default = False)

    class Meta:
        db_table = u'user_permission'

    def __unicode__(self):
        return "User: %s" % self.user.username + ", Datastream: %s," % self.datastream.name + " Read: %s" % self.read + ", Write: %s" % self.write



class Organization(models.Model):
    name = models.CharField(max_length=64)
    members = models.ManyToManyField(User)
    devices = models.ManyToManyField(Device, null = True, blank = True)
    suborganizations = models.ManyToManyField("self", symmetrical = False, null = True, blank = True)

    class Meta:
        db_table = u'organization'

    def __unicode__(self):
        return self.name 


