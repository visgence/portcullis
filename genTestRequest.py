#!/usr/bin/python

import sys
from urllib import urlencode, urlopen
import math
import time
import random

strf = "%Y-%m-%d"

params = {'auth_token': 'I want my baby back ribs.'}
while (True):
    i = time.time()
    print "Time = %s" % time.localtime(i)

    params['datastream_id'] = 15
    params['value'] = 50 * math.sin(i*math.pi/(86400))
    resp = urlopen('http://localhost:8000/collector/add_reading/?%s' % urlencode(params))
    print 'Http Response: '
    print resp.read()
    print
    time.sleep(1)

print 'Done'
