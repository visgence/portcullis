# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

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

class Device(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    ip_address = models.IPAddressField()

    class Meta:
        db_table = u'device'

    def __unicode__(self):
        return self.name

#Goes with Key
'''
class KeyManager(models.Manager):
    def validate(self, key):
        try:
            Key.objects.get(key = key)
            return True
        except ObjectDoesNotExist:
            return False
'''

#TODO: Use keys to validate user, devices, streams etc
'''
class Key(models.Model):
    key = models.CharField(primary_key=True, max_length=64)
    user = models.ForeignKey(User, null = True, blank = True)
    device = models.ForeignKey(Device, null = True, blank = True)
    description = models.TextField(null = True, blank = True)
    objects = KeyManager()

    class Meta:
        db_table = u'key'

    def get_type(self):
        if(self.device):
            return self.device
        elif(self.user):
            return self.user
        else:
            return None

    def __unicode__(self):
        return self.key 
'''

#TODO: Be able to grab all Data Streams by key that are writable/readable to etc.
'''
class DataStreamManager(models.Manager):
    def get_all_writable(self, key):
        if(Key.objects.validate(key) == False):
            return []

        valid_key = Key.objects.get(key = key)
        key_type = valid_key.get_type()

        if(key_type == None):
            return []
        
        streams = key_type.datastreams

        return 
'''

class DataStream(models.Model):
    id = models.AutoField(primary_key=True, db_column='datastream_id')
    node_id = models.IntegerField(null=True, blank=True)
    port_id = models.IntegerField(null=True, blank=True)
    units = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=64, blank=True)
    color = models.CharField(max_length=32, blank=True)
    min_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    max_value = models.DecimalField(null=True, max_digits=20,decimal_places=6, blank=True)
    scaling_function = models.ForeignKey(ScalingFunction, null=True, db_column='scaling_function', blank=True)
    reduction_type = models.CharField(max_length=32, blank=True)
    is_public = models.BooleanField()
    users = models.ManyToManyField(User, through='UserPermission')
    devices = models.ManyToManyField(Device, through='DevicePermission')
    #objects = DataStreamManager()


    class Meta:
        db_table = u'data_streams'

    def __unicode__(self):
        return " Node: %s," % self.node_id + " Port: %s," % self.port_id + " Name: " + self.name

class SensorReading(models.Model):
    id = models.AutoField(primary_key=True, db_column='read_id', editable=False)
    datastream = models.ForeignKey(DataStream)
    sensor_value = models.DecimalField(null=True, max_digits=6, decimal_places=0, blank=True)
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


