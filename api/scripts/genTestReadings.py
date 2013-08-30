#!/usr/bin/python

#Django environment setup
import os,sys
sys.path.insert(0, os.path.expanduser('../../'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'settings')

#Django imports
from django.contrib.auth import get_user_model
AuthUser = get_user_model()

#Local imports
from graphs.models import Sensor, DataStream, ClaimedSensor
from api.views.reading_loader import insert_reading

#System imports
import math
import time
import random
import sys


strf = "%Y-%m-%d"

foundSensors = []
foundStreams = []
sensors = ['sensor_one_id', 'sensor_two_id', 'sensor_three_id', 'sensor_four_id']


if len(sys.argv) > 1:
    startTime = int(time.mktime(time.strptime(sys.argv[1], strf)))
else:
    print 'You must give a date in the format: YYYY-MM-DD'
    sys.exit(1)

#Get some devices to test

for sensor in sensors:
    try:
        s = Sensor.objects.get(uuid=sensor)
        foundSensors.append(s)
    except Sensor.DoesNotExist:
        pass

for sensor in foundSensors:
    try:
        cs = ClaimedSensor.objects.get(sensor=sensor)
        ds = DataStream.objects.get(claimed_sensor=cs)
        foundStreams.append(ds)
    except DataStream.DoesNotExist:
        msg = "Could not find Datastream for ClaimedSensor %s. Aborting" % str(cs)
        sys.exit(msg)
    except ClaimedSensor.DoesNotExist:
        msg = "Could not find ClaimedSensor for sensor %s. Aborting" % str(sensor)
        sys.exit(msg)


if len(foundSensors) <= 0:
    msg = "Out of the possible test Sensors " + ", ".join(sensors)
    msg += " not a single one was found. Aborting"
    sys.exit(msg)


print "Found Sensors " +", ".join(map(lambda d: str(d.uuid), foundSensors))
print "Found Streams " +", ".join(map(lambda d: str(d.pk), foundStreams))


for t in range(startTime, startTime + 60*60*24*31, 1000*60):
    print "Time = %s" % time.localtime(t)

    for i in range(t, t + 1000*60, 60):

        for si, sensor in enumerate(foundSensors):
            
            if si % 2 == 0:
                value = 50 * math.sin(i*math.pi/(86400))
                insert_reading(foundStreams[si], sensor, value, i)
            elif si % 3 == 0:
                value = 50 * math.sin(i*2*math.pi/(60*60*24*30)) * math.sin(i*math.pi/(86400))
                insert_reading(foundStreams[si], sensor, value, i)
            else:
                value = random.randint(0, 50) * math.sin(i*math.pi/(86400))
                insert_reading(foundStreams[si], sensor, value, i)

    time.sleep(1)

print 'Done'
