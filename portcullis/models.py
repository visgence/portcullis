#System Imports
from django.db import models
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ObjectDoesNotExist



class ScalingFunctionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name = name)

class ScalingFunction(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    definition = models.CharField(max_length=1000, blank=True)
    objects = ScalingFunctionManager()

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
    owner = models.ForeignKey(User)
    objects = KeyManager()


    def __unicode__(self):
        return self.key + " Owned by %s" + self.owner.username




class DeviceManager(models.Manager):
    def get_by_key(self, key):
        return Device.objects.get(key = key)

class Device(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null = True, blank = True)
    ip_address = models.CharField(null = True, blank = True, max_length=18)
    key = models.OneToOneField(Key, null = True, blank = True)
    owner = models.ForeignKey(User)
    objects = DeviceManager()

    class Meta:
        unique_together = (('name', 'owner'),)

    def __unicode__(self):
        return self.name + " Owned by %s" + self.owner.username




class DataStreamManager(models.Manager):

    def get_writable_by_device(self, device):
        return DataStream.objects.filter(devicepermission__device = device, devicepermission__write = True)

    def get_writable_by_key(self, key):
        device = Device.objects.get_by_key(key)
        return DataStream.objects.filter(devicepermission__device = device, devicepermission__write = True)

class DataStream(models.Model):
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
        ordering = ['node_id', 'port_id', 'id']

    def __unicode__(self):
        return "Stream_ID: %s" % self.id  + " Node: %s," % self.node_id + " Port: %s," % self.port_id + " Name: " + self.name



class SensorReading(models.Model):
    id = models.CharField(primary_key=True,max_length=32)
    datastream = models.ForeignKey(DataStream)
    sensor_value = models.DecimalField(db_index = True, max_digits=20, decimal_places=6)
    date_entered = models.IntegerField(db_index = True)


    def __unicode__(self):
        return self.datastream.name + ", Value: %s," % self.sensor_value + " Date Entered: %s" % self.date_entered



class Permission(models.Model):
    read = models.BooleanField(default = True)
    write = models.BooleanField(default = False)

    class Meta:
        abstract = True



class DevicePermissionManager(models.Manager):
    def get_by_natural_key(self, stream, device):
        return self.get(datastream=stream, device=device)

class DevicePermission(Permission):
    datastream = models.ForeignKey(DataStream)
    device = models.ForeignKey(Device)
    objects = DevicePermissionManager()

    class Meta:
        unique_together = (('datastream', 'device'),)

    def __unicode__(self):
        return "Device: %s" % self.device.name + ", Datastream: %s," % self.datastream.name + " Read: %s" % self.read + ", Write: %s" % self.write



class UserPermissionManager(models.Manager):
    def get_by_natural_key(self, stream, user):
        return self.get(datastream=stream, user=user)

class UserPermission(Permission):
    datastream = models.ForeignKey(DataStream)
    user = models.ForeignKey(User)
    owner = models.BooleanField(default = False)
    objects = UserPermissionManager()

    class Meta:
        unique_together = (('datastream', 'user'),)

    def __unicode__(self):
        return "User: %s" % self.user.username + ", Datastream: %s," % self.datastream.name + " Read: %s" % self.read + ", Write: %s" % self.write



class Organization(models.Model):
    name = models.CharField(max_length=64)
    members = models.ManyToManyField(User)
    devices = models.ManyToManyField(Device, null = True, blank = True)
    suborganizations = models.ManyToManyField("self", symmetrical = False, null = True, blank = True)


    def __unicode__(self):
        return self.name 


