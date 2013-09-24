
#Django Imports
from django.db import models
from django.conf import settings
from django.utils import timezone

# System Imports
from base64 import urlsafe_b64encode as b64encode
import hashlib
import random
import string
import time
try:
    import simplejson as json
except ImportError:
    import json

# Local Imports
from graphs.data_reduction import reduction_type_choices
from chucho.models import ChuchoManager
from portcullis.models import PortcullisUser


class ScalingFunctionManager(ChuchoManager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

    def get_viewable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all scaling functions that can be viewed or assigned by a specified portcullis user.
        '
        ' Keyword Arguements:
        '   user - ScalingFuntion to filter scaling functions by.
        '
        ' Return: QuerySet of ScalingFunctions that are viewable by the specified PortcullisUser.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))


        if filter_args is not None and len(filter_args) > 0:
            return self.advanced_search(**filter_args)
        elif omni is not None:
            return self.search(omni)
        else:
            return self.all()


    def get_editable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all scaling functions that can be edited by a specified portcullis user.
        '
        ' Keyword Arguements:
        '   user - ScalingFuntion to filter editable scaling functions by.
        '
        ' Return: QuerySet of ScalingFunctions that are editable by the specified PortcullisUser.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if user.is_superuser:
            if filter_args is not None and len(filter_args) > 0:
                return self.advanced_search(**filter_args)
            elif omni is not None:
                return self.search(omni)
            else:
                return self.all()

        return self.none()

    def get_editable_by_pk(self, user, pk):
        '''
        ' Get's an instance of ScalingFunction specified by a pk if the given user is allowed to edit it.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the scaling function can be edited by them.
        '   pk   - Primary key of ScalingFunction to get.
        '
        ' Return: ScalingFunction that user is allowed to edit or None if not.
        '''
        #TODO: This will need to be updated once we add some kind of ownership to scaling functions.

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if not user.is_superuser:
            return None

        try:
            sf = self.get(pk=pk)
        except ScalingFunction.DoesNotExist:
            raise ScalingFunction.DoesNotExist("A scaling function does not exist for the primary key %s." % str(pk))

        return sf


class ScalingFunction(models.Model):
    name = models.CharField(max_length=32, unique=True, db_index=True)
    definition = models.CharField(max_length=1000)
    objects = ScalingFunctionManager()


    column_options = {
            'id': {'grid_column': False},
    }
    # Omni search columns
    search_fields = ['name']
    def __unicode__(self):
        return self.name

    def can_view(self, user):
        '''
        ' Checks if a ScalingFunction instance is allowed to view/read a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the scaling function can be viewed them.
        '
        ' Return: True if user is allowed to view and False otherwise.
        '''
        #TODO: Currently all users can read/view scaling functions. Maybe different when permissions become
        #      more robust.

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        return True

    def is_editable_by_user(self, user):
        '''
        ' Checks if a ScalingFunction instance is allowed to edited by a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the scaling function can be edited by them.
        '
        ' Return: True if user is allowed to edit and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if user.is_superuser:
            return True
       
        return False


class SensorManager(ChuchoManager):
    def can_edit(self, user):
        '''
        ' Checks if a PortcullisUser is allowed to edit or add instances of this model.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check permission for.
        '
        ' Return: True if user is allowed to edit objects of this model and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        return True


    def genSensorHash(self, username=''):
        '''
        ' return a hashed string to use for a sensor
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


    def get_viewable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all sensors that can be viewed or assigned by a specified portcullis user.
        '
        ' Super users will have access to all sensorss. (users with is_superuser = true)
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter sensors by.
        '
        ' Return: QuerySet of sensors that are viewable by the specified PortcullisUser.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if filter_args is not None and len(filter_args) > 0:
            objs = self.advanced_search(**filter_args)
        elif omni is not None:
            objs = self.search(omni)
        else:
            objs = self.all()
       
        return objs 


    def get_editable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all sensors that can be edited by a specified portcullis user.
        '
        ' Super users will have access to all sensors for editing. (users with is_superuser = true)
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter editable sensors by.
        '
        ' Return: QuerySet of sensors that are editable by the specified PortcullisUser.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if filter_args is not None and len(filter_args) > 0:
            objs = self.advanced_search(**filter_args)
        elif omni is not None:
            objs = self.search(omni)
        else:
            objs = self.all()

        return objs


class Sensor(models.Model):
    uuid = models.TextField(primary_key=True)
    sensor_type = models.TextField(blank=True)
    units = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    _metadata = models.TextField(blank=True)

    objects = SensorManager()

    column_options = {
        'uuid': {'_editable': True}
        ,'_metadata': {'grid_column': False, '_editable': False}
        }

    def can_view(self, user):
        '''
        ' Checks if a Key instance is allowed to view/read a key or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the key can be viewed them.
        '
        ' Return: True if user is allowed to view and False otherwise.
        '''
        #TODO: Needs to be improved later.

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))
 
        return True

    def get_editable_by_pk(self, user, pk):
        '''
        ' Get's an instance of Sensor specified by a pk if the given user is allowed to edit it.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the sensor can be edited by them.
        '   pk   - Primary key of sensor to get.
        '
        ' Return: sensor that user is allowed to edit or None if not.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        try:
            sensor = self.get(pk=pk)
        except Sensor.DoesNotExist:
            raise Sensor.DoesNotExist("A Sensor does not exist for the primary key %s" % str(pk))

        return sensor

    def toDict(self):
        data = {
            'uuid': self.uuid
            ,'sensor_type': self.sensor_type
            ,'units': self.units
            ,'description': self.description
        }

        return data

    def isClaimed(self):
        try:
            self.datastream_set.get(sensor=self)
            return True
        except DataStream.DoesNotExist:
            return False
        except Exception:
            return False

    def getMetadata(self):
        if self._metadata == '':
            return {}
        return json.loads(self._metadata)
    
    def setMetadata(self, data):
        if data == '' or data is None:
            data = {}

        self._metadata = json.dumps(data)

    def save(self, *args, **kwargs):
        super(Sensor, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.uuid

    metadata = property(getMetadata, setMetadata) 


class DataStreamManager(ChuchoManager):
    def can_edit(self, user):
        '''
        ' Checks if a PortcullisUser is allowed to edit or add instances of this model.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check permission for.
        '
        ' Return: True if user is allowed to edit objects of this model and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        return True

    def get_viewable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all DataStreams viewable or assignable by a PortcullisUser.
        '
        ' If user is a superuser (i.e is_superuser == true) then all streams are returned.
        ' Otherwise all valid keys for the user are used to filter DataSreams by.
        '
        ' Keyword Arguements:
        '   user - PortcullisUsert o filter DataStreams by.
        '
        ' Return: QuerySet of DataStreams that are viewable by the PortcullisUser.
        '''

        #Validate object is a PortcullisUser.
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser." % str(user))

        if filter_args is not None and len(filter_args) > 0:
            objs = self.advanced_search(**filter_args)
        elif omni is not None:
            objs = self.search(omni)
        else:
            objs = self.all()

        #Superusers get everything they don't own.
        if user.is_superuser:
            return objs

        return objs.filter(owner=user)
        
    def get_ds_and_validate(self, ds_id, obj, perm='read'):
        '''
        ' Return a DataStream that corresponds to the datastream id given if the obj has
        ' the specified permision.
        '
        ' Keyword args:
        '   ds_id - DataStream Id of the datastream wanted.
        '   obj - The object asking for permission.  Should either be a Key or PorcullisUser.
        '   perm - The permission wanted.  Current valid options are 'read' and 'post'.
        '
        ' Return: The corresponding datastream for the given permission if the permission permits
        '         or None.
        '''

        try:
            # First try to use the datastream_id
            ds = DataStream.objects.get(id=ds_id)
        except DataStream.DoesNotExist:
            raise DataStream.DoesNotExist("There is no DataStream for the id %s" % str(ds_id))

        if perm.lower() == 'read':
            if not ds.can_view(obj):
                return '%s cannot read DataStream %s!' % (str(obj), str(ds.id))
        elif perm.lower() == 'post':
            if not ds.canPost(obj):
                return '%s cannot post to DataStream %s!' % (str(obj), str(ds.id))
        else:
            raise ValueError('%s is an invalid permission type.' % str(perm))

        return ds

    def get_editable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all DataStreams that can be edited for a specified portcullis user.
        '
        ' Super users will have access to all DataStreams for editing. (users with is_superuser = true)
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter editable DataStreams by.
        '
        ' Return: QuerySet of DataStreams that are editable by the specified PortcullisUser.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))


        if filter_args is not None and len(filter_args) > 0:
            objs = self.advanced_search(**filter_args)
        elif omni is not None:
            objs = self.search(omni)
        else:
            objs = self.all()

        if user.is_superuser:
            return objs

        return objs.filter(device__owner=user)

    def get_editable_by_pk(self, user, pk):
        '''
        ' Get's an instance of DataStream specified by a pk if the given user is allowed to edit it.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the data stream can be edited by them.
        '   pk   - Primary key of DataStream to get.
        '
        ' Return: DataStream that user is allowed to edit or None if not.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        try:
            ds = self.get(pk=pk)
        except DataStream.DoesNotExist:
            raise DataStream.DoesNotExist("A Data Stream does not exist for the primary key %s" % str(pk))

        if user.is_superuser or ds.device.owner == user:
            return ds
        
        return None

    def claimedBySensor(self, sensor):
        '''
        '  Checks to see if a sensor instance is claimed or not.
        '
        '  Keyword Args:
        '     sensor - Sensor instance to check
        '
        '  Returns: DataStream instance that has claimed the sensor or None if sensor is un-claimed
        '''

        if not isinstance(sensor, Sensor):
            return None

        try:
            return self.get(sensor=sensor)
        except DataStream.DoesNotExist:
            return None


class DataStream(models.Model):
    sensor = models.ForeignKey(Sensor, unique=True, null=True, db_index=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    color = models.CharField(max_length=32, blank=True)
    min_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    max_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    reduction_type = models.CharField(max_length=32, default='sample', choices=reduction_type_choices())
    is_public = models.BooleanField(default=False)
    scaling_function = models.ForeignKey(ScalingFunction)
    name = models.TextField()
    description = models.TextField(blank=True)
    units = models.CharField(max_length=32, blank=True)
    created = models.BigIntegerField(default=time.time(), editable=False)
    _metadata = models.TextField(blank=True)

    objects = DataStreamManager()

    column_options = {
        'scaling_function': {'grid_column': False}
        ,'_metadata': {'grid_column': False, '_editable': False}
    }

    # For omni search
    search_fields = ['id', 'name', 'owner', 'units']

    class Meta:
        ordering = ['id']
        unique_together = (('owner', 'name'),)

    def __unicode__(self):
        return "Stream_ID: %s" % self.id  + " Name: " + self.name

    def toDict(self):
        data = {
            'sensor': None
            ,'id': self.id
            ,'owner': self.owner.email
            ,'name': self.name
        }

        if self.sensor is not None:
            data['sensor'] = self.sensor.toDict()

        return data

    def is_editable_by_user(self, user):
        '''
        ' Checks if a DataStream instance is allowed to edited by a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the data stream can be edited by them.
        '
        ' Return: True if user is allowed to edit and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if user.is_superuser or user == self.device.owner:
            return True

        return False

    def can_view(self, user):
        '''
        ' Return True if the user has permission to read this DataStream, False otherwise.
        '
        ' Keyword args:
        '    user - Returns True if the user is allowed to view the datastream. Returns false otherwise.
        '''
        
        if self.is_public:
            return True

        if isinstance(user, PortcullisUser) and (user == self.owner or user.is_superuser):
            return True

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
            if obj == self.device.owner or obj.is_superuser:
                return True
        if obj == self.device:
            return True

        return False

    def getMetadata(self):
        if self._metadata == '':
            return {}
        return json.loads(self._metadata)
    
    def setMetadata(self, data):
        if data == '' or data is None:
            data = {}

        self._metadata = json.dumps(data)
    
    metadata = property(getMetadata, setMetadata) 


class SensorReading(models.Model):
    datastream = models.ForeignKey(DataStream, blank=True, null=True, db_index=True)
    sensor = models.ForeignKey(Sensor, blank=True, null=True, db_index=True)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    timestamp = models.BigIntegerField(db_index=True)

    class Meta:
        unique_together = ('datastream', 'timestamp')

    def save(self, *args, **kwargs):
        super(SensorReading, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.datastream.name + ", Value: %s," % self.value + " Date Entered: %s" % self.timestamp

