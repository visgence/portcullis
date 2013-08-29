#System Imports
from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from chucho.models import ChuchoManager
import re

# Local Imports


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
        
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        self.email = self.email.strip()
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
