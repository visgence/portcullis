#!/usr/bin/python
import os,sys
sys.path.insert(0, os.path.expanduser('../'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'settings')
import netsnmp
from snmpPoller.models import *


streams = SnmpStream.objects.filter(active=True)

for s in streams:
    print "Polling %s oid=%s" % (s.host.hostname,s.oid)