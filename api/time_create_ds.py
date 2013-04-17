import string
import requests
import json
from time import time
import random

time0 = time()
# Generate a list of dictionaries to create new datastreams
key = 'uVRa5QQlWqXp8KWJ69ayRg=='
payload = [{'ds_data':{'name': ''.join(random.choice(string.printable) for x in range(20)), 'scaling_function':'identity', 'is_public': True, 'units': 'Derps'}} for z in range(5)]

time1 = time()
resp = requests.post('http://localhost:8080/api/create/', {'jsonData': json.dumps({'key': key, 'datastreams':payload}) })
print 'Request time: %f' % (time() - time1)

f = open('time_log.txt', 'w')
f.write(resp.content)

try:
    data = resp.json()
    print 'Create time: %f' % data['time']
except Exception as e:
    print 'Invalid json: ' + str(e)

f.close()
print 'Done.'
print 'Response in time_log.txt'
