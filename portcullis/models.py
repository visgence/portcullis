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


class ScalingFunction(models.Model):
    id = models.AutoField(primary_key=True, db_column='function_id')
    name = models.CharField(max_length=32, unique=True, blank=True)
    definition = models.CharField(max_length=1000, blank=True)

    class Meta:
        db_table = u'scaling_functions'
    def __unicode__(self):
        return "Name: " + self.name + ", ID: %s," % self.id + " Definition: %s" % self.definition 

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
    users = models.ManyToManyField(User, through='Permission')


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
    datastream = models.ForeignKey(DataStream)
    user = models.ForeignKey(User)
    owner = models.BooleanField(default = False)
    read = models.BooleanField(default = True)
    write = models.BooleanField(default = False)

    class Meta:
        db_table = u'permission'

    def __unicode__(self):
        return "User: %s" % self.user.username + ", Datastream: %s," % self.datastream.name + " Read: %s" % self.read + ", Write: %s" % self.write


class Organization(models.Model):
    name = models.CharField(max_length=64, blank=True)
    members = models.ManyToManyField(User)
    suborganization = models.ManyToManyField("self", symmetrical = False, null = True, blank = True)

    class Meta:
        db_table = u'organization'

    def __unicode__(self):
        return "Name: %s" % self.name 

