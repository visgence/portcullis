#!/usr/bin/python

import sys
from urllib import urlencode, urlopen
import math
import time
import random

strf = "%Y-%m-%d"

#if len(sys.argv) > 1:
#    startTime = int(time.mktime(time.strptime(sys.argv[1], strf)))
#else:
#    print 'You must give a date in the format: YYYY-MM-DD'
#    sys.exit(1)

#if len(sys.argv) > 2:
#    nMonths = int(sys.argv[2])
#else:
#    nMonths = 1


params = {'auth_token': 'I want my baby back ribs.'}
#for t in range(startTime, startTime + 60*60*24*31*nMonths, 1000*60):
while (True):
    i = time.time()
    print "Time = %s" % time.localtime(i)

    #for i in range(t, t + 1000*60, 60):
    params['datastream_id'] = 1
    params['value'] = 50 * math.sin(i*math.pi/(86400))
    resp = urlopen('http://localhost:8000/collector/add_reading/?%s' % urlencode(params))
    print 'Http Response: '
    print resp.readline()
    print
    time.sleep(1)

print 'Done'
