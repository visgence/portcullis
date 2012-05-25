# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from portcullis.models import DataStream


class Host(models.Model):
    hostname = models.CharField(max_length=64, unique=True, blank=False)
    version = models.IntegerField(max_length=2, choices=((1,"1"),(2,"2c"),(3,"3")))
    community = models.CharField(max_length=64,blank=False)
    def __unicode__(self):
        return "Host: hostname=%s version=%s community=%s" % (self.hostname,self.version,self.community)


class SnmpStream(models.Model):
    active = models.BooleanField()
    dataStream = models.ForeignKey(DataStream)
    host = models.ForeignKey(Host)
    oid = models.CharField(max_length=128)
    lastTime = models.DateField(auto_now=False,null=True,blank=True)
    lastValue = models.BigIntegerField(null=True,blank=True)
    maxTime = models.IntegerField()
    maxValue = models.BigIntegerField()
    maxValPerPoll = models.BigIntegerField()
    
    def __unicode__(self):
        return "SnmpStream: dataStreamID=%s hostname=%s oid=%s lastTime=%s lastValue=%s" % (self.dataStream.id,self.host.hostname,self.oid,self.lastTime,self.lastValue)
