#System Imports
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone
from base64 import urlsafe_b64encode as b64encode
import hashlib
import random
import string
from datetime import timedelta

# Local Imports
from graphs.data_reduction import reduction_type_choices

class PortcullisUser(User):
    '''
    ' The class that defines users of the system.
    '''
    # TODO: Add custom user fields/methods

    pass

    
class ScalingFunctionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name = name)

class ScalingFunction(models.Model):
    name = models.CharField(max_length=32, unique=True)
    definition = models.CharField(max_length=1000)
    objects = ScalingFunctionManager()

    def __unicode__(self):
        return self.name



class KeyManager(models.Manager):
    def validate(self, token):
        # TODO: decide whether or not to keep this method, or to replace it (within other validation)
        # also whether to return different kinds of errors/etc.
        try:
            key = Key.objects.get(key = token)
        except ObjectDoesNotExist:
            return None

        key.use()
        if key.isCurrent():
            return key
        return None


    def genKeyHash(self, username = ''):
        '''
        ' return a hashed string to use for a key
        '
        ' Keyword arg:
        '   username - The user, if available, this string is for.  Does not have to be a
        '              username, can be any string.
        '''
        md5 = hashlib.md5()
        randomStr = ''.join(random.choice(string.printable) for x in range(20))
        md5.update(str(timezone.now()))
        md5.update(username)
        md5.update(randomStr)
        return b64encode(md5.digest())


    def generateKey(self, user, description = '', expiration = None, uses = None, readL = None, postL = None):
        '''
        ' Create a new (hopefully) unique key for the specified user, and return it.
        '
        ' Keyword Arguments:
        '  user - The PortcullisUser to create this key for.
        '  description - Short description of the purpose of this key.
        '  expiration - Datetime object that determines when this key is no longer valid.
        '               the default is None, which means it does not have an expiration date.
        '  uses - The number of times this key can be used before it expires.  0 means this key has no
        '         more uses.  None means it has infinite uses.  The default is None.
        '  readL - The list of DataStream (or possibly other) objects that can be read with this key.
        '          The default is None.
        '  postL - The list of DataStream (or other) objects that can be posted to with this key.
        '          The default is None.
        '''

        token = self.genKeyHash(user.username)
        key = Key.objects.create(key=token, owner=user, description=description,
                                 expiration=expiration, num_uses=uses)

        if readL is not None:
            for ds in readL:
                ds.can_read.add(key)

        if postL is not None:
            for ds in postL:
                ds.can_post.add(key)

        return key

class Key(models.Model):
    key = models.CharField(primary_key=True, max_length=1024, blank = True)
    description = models.TextField(blank = True)
    owner = models.ForeignKey(PortcullisUser)
    expiration = models.DateTimeField(null = True, blank = True)
    num_uses = models.IntegerField(null = True, blank = True)
    objects = KeyManager()

    def isCurrent(self):
        '''
        ' Check expiration, return True if this key is current, false if expired.
        ' There are 2 types of expiration.  The first is date.  The current date must be earlier than
        ' the expiration date.  The other is the number of uses.  The number of uses must be nonzero.
        ' A null expiration does not expire by date.
        '''
        if ((self.expiration is None or timezone.now() < self.expiration) and
            (self.num_uses is None or self.num_uses >= 0)):
            return True
        return False

    def use(self):
        '''
        ' When a key is used, decrement its num_uses by 1.
        '''
        if self.num_uses >= 0:
            self.num_uses -= 1
            self.save()

    def save(self, *args, **kwargs):
        if self.key is None or self.key == '':
            self.key = Key.objects.genKeyHash('generic_user')
        super(Key, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.key + " Owned by " + self.owner.username 


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
        return DataStream.objects.filter(can_post = device.key)

    def get_writable_by_key(self, key):
        return DataStream.objects.filter(can_post = key)

    def get_ds_and_validate(self, ds_id, obj, perm = 'read'):
        '''
        ' Return a DataStream that corresponds to the datastream id given if the obj has
        ' the specified permision.
        '
        ' Keyword args:
        '   ds_id - DataStream Id of the datastream wanted.  For purposes of backwards compatibility
        '           this can also be a tuple of (node_id, port_id).
        '   obj - The object asking for permission.  Should either be a Key or PorcullisUser.
        '   perm - The permission wanted.  Current valid options are 'read' and 'post'.
        '''
        if isinstance(ds_id, tuple):
            try:
                # If that fails, try the node/port combination.  This is for backwards compatability,
                # but since these fields are not unique together, it is dangerous.
                ds = DataStream.objects.get(node_id = ds_id[0], port_id = ds_id[1])
            except ObjectDoesNotExist:
                return 'Invalid node/port combination.'
            except MultipleObjectsReturned:
                return 'Multiple Objects Returned.  Node/Port are no longer unique together.  Please use a DataStream id.'

        else:
            try:
                # First try to use the datastream_id
                ds = DataStream.objects.get(id = ds_id)
            except ObjectDoesNotExist:
                return 'Invalid DataStream!'

        if perm == 'read':
            if not ds.canRead(obj):
                return '%s cannot read DataStream %s!' % (str(obj), str(ds.id))
        elif perm == 'post':
            if not ds.canPost(obj):
                return '%s cannot post to DataStream %s!' % (str(obj), str(ds.id))
        else:
            return '%s is an invalid permission type.' % str(perm)
            
        return ds

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

    def canRead(self, obj):
        '''
        ' Return True if the obj has permission to read this DataStream, False otherwise.
        '
        ' Keyword args:
        '    obj - The object to check for permission to read for.
        '          Any object can read a public datastream.
        '          Providing a key in the can_read M2M field will return true.
        '          Providing a PortcullisUser that either owns the datastream or
        '           owns a key that is in the can_read M2M field will return true.
        '          Returns false otherwise.
        '''
        if self.is_public == True:
            return True

        if isinstance(obj, PortcullisUser):
            if obj == self.owner:
                return True
            elif obj.id in self.can_read.filter( (Q(expiration__gt = timezone.now()) | Q(expiration = None)) &
                                                (Q(num_uses__gt = 0) | Q(num_uses = None))
                                                 ).values_list('owner', flat = True):
                return True
        
        if isinstance(obj, Key):
            if obj.isCurrent():
                return obj in self.can_read.all()
            else:
                return False

        return False

    def canPost(self, obj):
        '''
        ' Return True if the obj has permission to post to this DataStream, False otherwise.
        '
        ' Keyword args:
        '    obj - The object to check for permission to post for.
        '          Providing a key in the can_post M2M field will return true.
        '          Providing a PortcullisUser that either owns the datastream or
        '           owns a key that is in the can_post M2M field will return true.
        '          Returns false otherwise.
        '''
        if isinstance(obj, PortcullisUser):
            if obj == self.owner:
                return True
            elif obj.id in self.can_post.filter( (Q(expiration__gt = timezone.now()) | Q(expiration = None)) &
                                                (Q(num_uses__gt = 0) | Q(num_uses = None) )
                                                 ).values_list('owner', flat = True):
                return True
            else:
                return False
        
        if isinstance(obj, Key):
            if obj.isCurrent():
                return obj in self.can_post.all()
            else:
                return False
            
        return False
    
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


#Place holder model to expand when we support more widgets than just graphs.
class SavedWidget(models.Model):

    def __unicode__(self):
        return 'Widget: %s' % str(self.id)


class SavedView(models.Model):
    key = models.OneToOneField(Key, primary_key=True)
    widget = models.ManyToManyField(SavedWidget)
    # TODO: Should this be a Foreign key in the widget class? OneToMany?

    def __unicode__(self):
        return 'SavedView: %s, Owner: %s' % (self.key.key, self.key.owner)

'''
class Organization(models.Model):
    name = models.CharField(max_length=64)
    members = models.ManyToManyField(User)
    devices = models.ManyToManyField(Device, null = True, blank = True)
    suborganizations = models.ManyToManyField("self", symmetrical = False, null = True, blank = True)


    def __unicode__(self):
        return self.name 
'''
