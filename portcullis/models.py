#System Imports
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Local Imports
from graphs.data_reduction import reduction_type_choices

class PortcullisUser(User):
    # TODO: Add custom user fields/methods

    def can_read_stream(self, stream):
        '''The user instance has read permission on the given data stream.
        ' Keyword args:
        '  stream - The DataStream object checking permission for.
        '''
        if stream.is_public:
            return True

        if self == stream.owner:
            return True
        
        if self in stream.can_read.values_list('owner'):
            return True
    
        return False;

class ScalingFunctionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name = name)

class ScalingFunction(models.Model):
    name = models.CharField(max_length=32, unique=True)
    definition = models.CharField(max_length=1000)
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
    key = models.CharField(primary_key=True, max_length=1024)
    description = models.TextField(blank = True)
    owner = models.ForeignKey(PortcullisUser)
    expiration = models.DateTimeField(null = True, blank = True)
    num_uses = models.IntegerField(null = True, blank = True)
    objects = KeyManager()



    def __unicode__(self):
        return self.key + " Owned by %s" + self.owner.username




class DeviceManager(models.Manager):
    def get_by_key(self, key):
        return Device.objects.get(key = key)

class Device(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank = True)
    ip_address = models.IPAddressField(blank = True)
    key = models.ForeignKey(Key, null = True, blank = True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(PortcullisUser)
    objects = DeviceManager()

    class Meta:
        unique_together = (('name', 'owner'),)

    def __unicode__(self):
        return self.name + " Owned by %s" + self.owner.username



class DataStreamManager(models.Manager):

    def get_writable_by_device(self, device):
        return DataStream.objects.filter(can_write = device.key)

    def get_writable_by_key(self, key):
        device = Device.objects.get_by_key(key)
        return DataStream.objects.filter(can_write = device.key)

class DataStream(models.Model):
    node_id = models.IntegerField(null=True, blank=True)
    port_id = models.IntegerField(null=True, blank=True)
    units = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=64, blank=True)
    color = models.CharField(max_length=32, blank=True)
    min_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    max_value = models.DecimalField(null=True, max_digits=20,decimal_places=6, blank=True)
    scaling_function = models.ForeignKey(ScalingFunction)
    reduction_type = models.CharField(max_length=32, default='mean', choices=reduction_type_choices())
    is_public = models.BooleanField()
    owner = models.ForeignKey(PortcullisUser)
    # keys that have permission to read to this data stream
    can_read = models.ManyToManyField(Key, related_name = 'can_read_set', blank=True)
    # keys that have permission to post to this data stream
    can_post = models.ManyToManyField(Key, related_name = 'can_write_set', blank=True)
    objects = DataStreamManager()

    class Meta:
        ordering = ['node_id', 'port_id', 'id']

    def __unicode__(self):
        return "Stream_ID: %s" % self.id  + " Node: %s," % self.node_id + " Port: %s," % self.port_id + " Name: " + self.name


    
class SensorReading(models.Model):
    id = models.CharField(primary_key=True,max_length=32)
    datastream = models.ForeignKey(DataStream, db_index = True)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    timestamp = models.IntegerField(db_index = True)

    class Meta:
        unique_together = ('datastream', 'timestamp')

    def save(self, *args, **kwargs):
        self.id = str(self.datastream.id) + '_' + str(self.timestamp)
        super(SensorReading, self).save(*args, **kwargs)
        

    def __unicode__(self):
        return self.datastream.name + ", Value: %s," % self.value + " Date Entered: %s" % self.timestamp

'''
class Organization(models.Model):
    name = models.CharField(max_length=64)
    members = models.ManyToManyField(User)
    devices = models.ManyToManyField(Device, null = True, blank = True)
    suborganizations = models.ManyToManyField("self", symmetrical = False, null = True, blank = True)


    def __unicode__(self):
        return self.name 
'''
