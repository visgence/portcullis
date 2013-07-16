#System Imports
from django.db import models
from django.db.models import Q
from django.utils import timezone
from base64 import urlsafe_b64encode as b64encode
import hashlib
import random
import string
from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from chucho.models import ChuchoManager
from django.conf import settings
import re

# Local Imports
from graphs.data_reduction import reduction_type_choices


class PortcullisUserManager(BaseUserManager, ChuchoManager):
    '''
    ' Custom user manager for Portcullis User
    '''
    def create_user(self, email, first_name, last_name, password=None):
        user = PortcullisUser(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()

    def create_superuser(self, email, first_name, last_name, password):
        user = PortcullisUser(email=email, first_name=first_name, last_name=last_name, is_superuser=True)
        user.set_password(password)
        user.save()

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
       
        if user.is_superuser:
            return True

        return False

    def get_viewable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all Portcullis Users that can be viewed or assigned by a specified PortcullisUser.
        '
        ' Superusers (i.e user.is_superuser == true) can view/assign all PortcullisUsers while anyone
        ' else simply can view/assing themselves.
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter viewable PortcullisUsers' by.
        '
        ' Return: QuerySet of PortcullisUsers that are viewable by the specified PortcullisUser.
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

        return self.filter(pk=user.pk)

    def get_editable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all Portcullis Users that can be edited by a specified PortcullisUser.
        '
        ' Superusers (i.e user.is_superuser == true) can edit all PortcullisUsers while anyone
        ' else simply can edit themselves.
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter editable PortcullisUsers' by.
        '
        ' Return: QuerySet of PortcullisUsers that are editable by the specified PortcullisUser.
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

        return self.filter(pk=user.pk)


    def get_editable_by_pk(self, user, pk):
        '''
        ' Get's an instance of PortcullisUser specified by a pk if the given user is allowed to edit it.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the user can be edited by them.
        '   pk   - Primary key of PortcullisUser to get.
        '
        ' Return: PortcullisUser that user is allowed to edit or None if not.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        try:
            u = self.get(pk=pk)
        except PortcullisUser.DoesNotExist:
            raise PortcullisUser.DoesNotExist("A Portcullis User does not exist for the primary key %s." % str(pk))

        if user.is_superuser or u == user:
            return u

        return None

    def search(self, search_str, operator=None, column=None):
        ''' Overwrite ChuchoManager to handle our user'''
        print 'Searching: "%s"' % search_str
        # Regexes to trigger different kinds of searches.
        pattern_name1 = r'^\s*(.+)\s+(.+)\s*$'
        pattern_name2 = r'^\s*(.+),\s*(.+)\s*$'
        pattern_username = r'^\s*(.+)\s*$'
        #pattern_email = r'^\s*(\.*@.*)\s*$'

        q_list = []
        m = re.match(pattern_name1, search_str, re.I)
        if m is not None:
            q_list.append(Q(first_name__icontains=m.group(1), last_name__icontains=m.group(2)))

        m = re.match(pattern_name2, search_str, re.I)
        if m is not None:
            q_list.append(Q(first_name__icontains=m.group(2), last_name__icontains=m.group(1)))

        m = re.match(pattern_username, search_str, re.I)
        if m is not None:
            q_list.append(Q(email__icontains=m.group(1)))
            q_list.append(Q(first_name__icontains=m.group(1)))
            q_list.append(Q(last_name__icontains=m.group(1)))

        # m = re.match(pattern_email, search_str, re.I)
        # if m is not None:
        #     q_list.append(Q(email__icontains=m.group(1)))

        q_all = None
        for q in q_list:
            if q_all is None:
                q_all = q
            else:
                q_all |= q
        if q_all is None:
            return self.none()
        else:
            return self.filter(q_all)


class PortcullisUser(AbstractBaseUser):
    '''
    ' The class that defines users of the system.
    '''
    email = models.CharField(max_length=128, unique=True, db_index=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now(), editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'is_superuser', 'is_staff']

    objects = PortcullisUserManager()

    column_options = {
            'id': {'grid_column': False},
            'password': {'_type': 'password', 'grid_column': False},
            'last_login': {'_editable': False}
    }
    
    search_fields = ['email', 'first_name', 'last_name', 'date_joined']

    def get_full_name(self):
        '''
        ' Returns the first and last name.
        '''
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        '''
        ' Returns only the first name
        '''
        return self.first_name

    def save(self, *args, **kwargs):
        '''
        ' Overwritten save method to get around not null constraint on 2 fields, that cannot
        ' be overwritten from PortcullisUser
        '''
        if self.last_login is None:
            self.last_login = datetime(1900, 1, 1).replace(tzinfo=timezone.utc)
        if self.date_joined is None:
            self.date_joined = timezone.now()
        super(PortcullisUser, self).save(*args, **kwargs)

    def can_view(self, user):
        '''
        ' Checks if a PortcullusUser instance is allowed to view/read a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the user can be viewed them.
        '
        ' Return: True if user is allowed to view and False otherwise.
        '''
        #TODO: currently just a wrapper until our permissions become more robust.

        return self.is_editable_by_user(user)

    def is_editable_by_user(self, user):
        '''
        ' Checks if a PortcullusUser instance is allowed to edited by a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the user can be edited by them.
        '
        ' Return: True if user is allowed to edit and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if user.is_superuser or user == self:
            return True

        return False


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
    name = models.CharField(max_length=32, unique=True)
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


class KeyManager(ChuchoManager):
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

    def validate(self, token):
        # TODO: decide whether or not to keep this method, or to replace it (within other validation)
        # also whether to return different kinds of errors/etc.
        try:
            key = Key.objects.get(key=token)
        except Key.DoesNotExist:
            return None

        if key.isCurrent():
            key.use()
            return key
        return None

    def genKeyHash(self, username=''):
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

    def generateKey(self, user, description='', expiration=None, uses=None, readL=None, postL=None):
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

        token = self.genKeyHash(user.get_username())
        key = Key.objects.create(key=token, owner=user, description=description,
                                 expiration=expiration, num_uses=uses)

        if readL is not None:
            for ds in readL:
                ds.can_read.add(key)

        if postL is not None:
            for ds in postL:
                ds.can_post.add(key)

        return key

    def get_viewable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all keys that can be viewed or assigned by a specified portcullis user.
        '
        ' Super users will have access to all keys. (users with is_superuser = true)
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter keys by.
        '
        ' Return: QuerySet of Keys that are viewable by the specified PortcullisUser.
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
       
        if not user.is_superuser:
            objs = objs.filter(owner=user)
            
        validKeys = []
        for key in objs:
            if key.isCurrent():
                validKeys.append(key.key)

        return self.filter(key__in=validKeys)

    def get_editable(self, user, filter_args=None, omni=None):
        '''
        ' Gets all keys that can be edited by a specified portcullis user.
        '
        ' Super users will have access to all keys for editing. (users with is_superuser = true)
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter editable keys by.
        '
        ' Return: QuerySet of Keys that are editable by the specified PortcullisUser.
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

        return objs.filter(owner=user)

    def get_editable_by_pk(self, user, pk):
        '''
        ' Get's an instance of Key specified by a pk if the given user is allowed to edit it.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the key can be edited by them.
        '   pk   - Primary key of Key to get.
        '
        ' Return: Key that user is allowed to edit or None if not.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        try:
            key = self.get(key=pk)
        except Key.DoesNotExist as e:
            raise Key.DoesNotExist("A key does not exist for the primary key %s" % str(pk))

        if user.is_superuser or key.owner == user:
            return key

        return None


class Key(models.Model):
    key = models.CharField(primary_key=True, max_length=1024, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    expiration = models.DateTimeField(null=True, blank=True)
    num_uses = models.IntegerField(null=True, blank=True)
    objects = KeyManager()

    column_options = {
        'key': {'_editable': True}
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

        if not self.isCurrent():
            return False
        
        if user.is_superuser:
            return True
       
        if user == self.owner:
            return True

        return False

    def is_editable_by_user(self, user):
        '''
        ' Checks if a Key instance is allowed to edited by a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the key can be edited by them.
        '
        ' Return: True if user is allowed to edit and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if user.is_superuser or user == self.owner:
            return True

        return False

    def isCurrent(self):
        '''
        ' Check expiration, return True if this key is current, false if expired.
        ' There are 2 types of expiration.  The first is date.  The current date must be earlier than
        ' the expiration date.  The other is the number of uses.  The number of uses must be nonzero.
        ' A null expiration does not expire by date.
        '''
        if ((self.expiration is None or timezone.now() < self.expiration) and
            (self.num_uses is None or self.num_uses > 0)):
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
        return self.key + " Owned by " + self.owner.get_username()


class DeviceManager(models.Manager):
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

    def get_viewable(self, user, filter_args=None):
        '''
        ' Gets all device that can be viewed or assigned by a specified portcullis user.
        '
        ' Super users will have access to all Devices. (users with is_superuser = true)
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter Devices by.
        '
        ' Return: QuerySet of Devices that are viewable by the specified PortcullisUser.
        '''

        #TODO: Wrapper until permissions become more robust

        return self.get_editable(user, filter_args)

    def get_editable(self, user, filter_args=None):
        '''
        ' Gets all device that can be edited by a specified portcullis user.
        '
        ' Super users will have access to all Devices for editing. (users with is_superuser = true)
        '
        ' Keyword Arguements:
        '   user - PortcullisUser to filter editable Devices by.
        '
        ' Return: QuerySet of Devices that are editable by the specified PortcullisUser.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if filter_args is not None:
            objs = self.advanced_search(**filter_args)
        else:
            objs = self.all()

        if user.is_superuser:
            return objs

        return objs.filter(owner=user)

    def get_editable_by_pk(self, user, pk):
        '''
        ' Get's an instance of Device specified by a pk if the given user is allowed to edit it.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the device can be edited by them.
        '   pk   - Primary key of Device to get.
        '
        ' Return: Device that user is allowed to edit or None if not.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        try:
            d = self.get(id=pk)
        except Device.DoesNotExist as e:
            raise Device.DoesNotExist("A device does not exist for the primary key %s." % str(pk))

        if user.is_superuser or d.owner == user:
            return d

        return None


class Device(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    ip_address = models.IPAddressField(blank=True)
    key = models.ForeignKey(Key, null=True, blank=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    objects = DeviceManager()

    def can_view(self, user):
        '''
        ' Checks if a Device instance is allowed to view/read a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the device can be viewed them.
        '
        ' Return: True if user is allowed to view and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        return True

    def is_editable_by_user(self, user):
        '''
        ' Checks if a Device instance is allowed to edited by a user or not.
        '
        ' Keyword Arguments:
        '   user - PortcullisUser to check if the device can be edited by them.
        '
        ' Return: True if user is allowed to edit and False otherwise.
        '''

        #Validate user object
        if not isinstance(user, PortcullisUser):
            raise TypeError("%s is not a PortcullisUser" % str(user))

        if user.is_superuser or user == self.owner:
            return True

        return False

    class Meta:
        unique_together = (('name', 'owner'),)

    def __unicode__(self):
        return self.name + " Owned by %s" + self.owner.get_username()


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

    def get_readable_by_key(self, key):
        '''
        ' Gets all DataStreams that can be read by a specified Key.
        '
        ' Validate Key which means that if the key has a number of uses left
        ' one will be subtracted from it.
        '
        ' Keyword Arguments:
        '   key - Key object to filter readable DataStreams by.
        '
        ' Return: QuerySet of DataStreams that are readable by the specified Key.
        '''

        #Validate object is a Key
        if not isinstance(key, Key):
            raise TypeError("%s is not a Key object." % str(key))

        #Make sure key is valid
        vKey = Key.objects.validate(key.key)
        if vKey is None:
            raise Exception("%s is not a valid key." % str(vKey))

        return DataStream.objects.filter(can_read=key)

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

        keys = Key.objects.filter(owner=user)
        validKeys = []
        for key in keys:
            if key.isCurrent():
                validKeys.append(key)

        return objs.filter(can_read__in=validKeys).distinct()
        
#        if user.is_superuser:
#            objs = self.all()
#        else:
#            keys = Key.objects.filter(owner=user)
#            validKeys = [key for key in keys if key.isCurrent()]
#            objs = self.filter(Q(can_read__in=validKeys) | Q(owner=user)).distinct()
#
#        if filter_args is not None and len(filter_args) > 0:
#            objs = objs.filter(**filter_args)
#        elif omni is not None:
#            objs = objs.search(omni)
#
#        return objs

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

        return objs.filter(owner=user)

        
#        if filter_args is not None and len(filter_args) > 0:
#            objs = self.filter(**filter_args)
#        elif omni is not None:
#            objs = self.search(omni)
#
#        if user.is_superuser:
#            objs = self.all()
#        else:
#            keys = Key.objects.filter(owner=user)
#            validKeys = [key for key in keys if key.isCurrent()]
#            objs = self.filter(Q(can_post__in=validKeys) | Q(owner=user)).distinct()
#
#        return objs

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

        keys = Key.objects.filter(owner=user)
        validKeys = [key for key in keys if key.isCurrent()]
        if user.is_superuser or ds.owner == user or not set(ds.can_post.all()).disjoint(validKeys):
            return ds
        
        return None


class DataStream(models.Model):
    units = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=128, db_index=True)
    description = models.CharField(max_length=64, blank=True)
    color = models.CharField(max_length=32, blank=True)
    min_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    max_value = models.DecimalField(null=True, max_digits=20, decimal_places=6, blank=True)
    scaling_function = models.ForeignKey(ScalingFunction)
    reduction_type = models.CharField(max_length=32, default='mean', choices=reduction_type_choices())
    is_public = models.BooleanField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    # keys that have permission to read to this data stream
    can_read = models.ManyToManyField(Key, related_name='can_read_set', blank=True)
    # keys that have permission to post to this data stream
    can_post = models.ManyToManyField(Key, related_name='can_write_set', blank=True)
    objects = DataStreamManager()

    column_options = {
        'description': {'grid_column': False},
        'color': {'grid_column': False},
        'scaling_function': {'grid_column': False},
        'reduction_type': {'grid_column': False},
        }

    # For omni search
    search_fields = ['id', 'name', 'owner', 'units']

    class Meta:
        ordering = ['id']
        unique_together = (('owner', 'name'),)

    def __unicode__(self):
        return "Stream_ID: %s" % self.id  + " Name: " + self.name

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

        if user.is_superuser or user == self.owner:
            return True

        return False

    def can_view(self, obj):
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
            if obj == self.owner or obj.is_superuser:
                return True
            elif obj.id in self.can_read.filter( (Q(expiration__gt=timezone.now()) | Q(expiration=None)) &
                                                (Q(num_uses__gt=0) | Q(num_uses=None))
                                                 ).values_list('owner', flat=True):
                return True

        elif isinstance(obj, Key):
            if obj.isCurrent():
                return obj in self.can_read.all()
            else:
                return False
        else:
            raise TypeError("%s is not a PortcullisUser or a Key" % str(obj))

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
            if obj == self.owner or obj.is_superuser:
                return True
            elif obj.id in self.can_post.filter( (Q(expiration__gt=timezone.now()) | Q(expiration=None)) &
                                                (Q(num_uses__gt=0) | Q(num_uses=None) )
                                                 ).values_list('owner', flat=True):
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
    id = models.CharField(primary_key=True, max_length=32)
    datastream = models.ForeignKey(DataStream, db_index=True)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    timestamp = models.IntegerField(db_index=True)

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
