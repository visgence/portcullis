#!/usr/bin/python

#Django environment setup
import os,sys
sys.path.insert(0, os.path.expanduser('./'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'settings')

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
AuthUser = get_user_model()
from portcullis.models import DataStream, ScalingFunction
from collector.views.data_loader import insert_reading

import math
import time
import random
import sys

strf = "%Y-%m-%d"

try:
    scaleF = ScalingFunction.objects.get(name='Identity')
    print 'Scaling Function good.'
except ObjectDoesNotExist:
    print 'I am creating a scaling function'
    scaleF = ScalingFunction(name = 'Identity', definition = 'return x;')
    scaleF.save()
    
try:
    ds1 = DataStream.objects.get(id=1)
except ObjectDoesNotExist:
    ds1 = DataStream(id = 1, name = 'Test data 1', description = 'Simple Sign curve',
                     color = 'purple', min_value = -50.0, max_value = 50.0, scaling_function = scaleF, 
                     owner = AuthUser.objects.get(username = 'portcullis'))
    ds1.save()

try:
    ds2 = DataStream.objects.get(id=2)
except ObjectDoesNotExist:
    ds2 = DataStream(id=2, name = 'Test data 2', description = 'Amplitude modulated sin curve.',
                     color = 'red   ', min_value = -50.0, max_value = 50.0, scaling_function = scaleF,
                     owner = AuthUser.objects.get(username = 'portcullis'))
    ds2.save()

try:
    ds3 = DataStream.objects.get(id=3)
except ObjectDoesNotExist:
    ds3 = DataStream(id=3, name = 'Test data 3', description = 'Random amplitude modulation',
                     color = 'blue', min_value = -50.0, max_value = 50.0, scaling_function = scaleF,
                     owner = AuthUser.objects.get(username = 'portcullis'))
    ds3.save()

if len(sys.argv) > 1:
    startTime = int(time.mktime(time.strptime(sys.argv[1], strf)))
else:
    print 'You must give a date in the format: YYYY-MM-DD'
    sys.exit(1)

if len(sys.argv) > 2:
    nMonths = int(sys.argv[2])
else:
    nMonths = 1
    
for t in range(startTime, startTime + 60*60*24*31*nMonths, 1000*60):
    print "Time = %s" % time.localtime(t)

    for i in range(t, t + 1000*60, 60):
        insert_reading(ds1, 50 * math.sin(i*math.pi/(86400)), i)
        insert_reading(ds2, 50 * math.sin(i*2*math.pi/(60*60*24*30)) * math.sin(i*math.pi/(86400)), i)
        insert_reading(ds3, random.randint(0, 50) * math.sin(i*math.pi/(86400)), i)
    time.sleep(1)

print 'Done'
