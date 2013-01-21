#!/usr/bin/python

import sys
from urllib import urlencode, urlopen
import math
import time
import random
try: import simplejson as json
except ImportError: import json

strf = "%Y-%m-%d"

if len(sys.argv) > 1:
    startTime = int(time.mktime(time.strptime(sys.argv[1], strf)))
else:
    print 'You must give a date in the format: YYYY-MM-DD'
    sys.exit(1)

if len(sys.argv) > 2:
    nMonths = int(sys.argv[2])
else:
    nMonths = 1


params = {'auth_token': 'I want my baby back ribs.'}
for t in range(startTime, startTime + 60*60*24*31*nMonths, 10*60):
    print "Time = %s" % time.localtime(t)

    data = []

    for i in range(t, t + 10*60, 60):
        node_id = 3
        port_id = 3
        value =  50 * math.sin(i*math.pi/(86400))
        data.append([node_id, port_id, value])

    params['json'] = json.dumps(data)

    resp = urlopen('http://localhost:8000/collector/add_reading_bulk/?%s' % urlencode(params))
    print 'Http Response: '
    print resp.read()
    print
    time.sleep(1)

print 'Done'
