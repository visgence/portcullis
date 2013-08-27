#!/usr/bin/python

#Django environment setup
import os,sys
sys.path.insert(0, os.path.expanduser('./'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'settings')

#Django imports
from django.contrib.auth import get_user_model
AuthUser = get_user_model()

#Local imports
from portcullis.models import Device
#from api.views.reading_loader import insert_reading

#System imports
import math
import time
import random
import sys


strf = "%Y-%m-%d"
foundDevices = []
d1, d2, d3, d4 = None


if len(sys.argv) > 1:
    startTime = int(time.mktime(time.strptime(sys.argv[1], strf)))
else:
    print 'You must give a date in the format: YYYY-MM-DD'
    sys.exit(1)

#Get some devices to test

try:
    d1 = Device.objects.get(uuid='device1')
    foundDevices.append(d1)
except Device.DoesNotExist:
    pass

try:
    d2 = Device.objects.get(uuid='device2')
    foundDevices.append(d2)
except Device.DoesNotExist:
    pass

try:
    d3 = Device.objects.get(uuid='device3')
    foundDevices.append(d3)
except Device.DoesNotExist:
    pass

try:
    d4 = Device.objects.get(uuid='device4')
    foundDevices.append(d4)
except Device.DoesNotExist:
    pass


if len(foundDevices) <= 0:
    msg = "Out of the possible test Devices device1, device2, device3, device4 "
    msg += " not a single one was found. Aborting"
    sys.exit(msg)

print "Found " +", ".join(map(lambda d: d.uuid, foundDevices))

for t in range(startTime, startTime + 60*60*24*31, 1000*60):
    print "Time = %s" % time.localtime(t)

    for i in range(t, t + 1000*60, 60):
        if d1 is not None:
            insert_reading(d1, 50 * math.sin(i*math.pi/(86400)), i)
        if d2 is not None:
            insert_reading(d2, 50 * math.sin(i*2*math.pi/(60*60*24*30)) * math.sin(i*math.pi/(86400)), i)
        if d3 is not None:
            insert_reading(d3, random.randint(0, 50) * math.sin(i*math.pi/(86400)), i)
        if d4 is not None:
            insert_reading(d4, random.randint(0, 50) * math.sin(i*math.pi/(86400)), i)

    time.sleep(1)

print 'Done'
