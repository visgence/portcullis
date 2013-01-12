#Django environment setup
import os,sys
sys.path.insert(0, os.path.expanduser('./'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'settings')

from portcullis.models import DataStream
from collector.data_loader import insert_reading

import math
import time

ds = DataStream.objects.get(id=1)
startTime = int(time.time())
for t in range(startTime, startTime + 60*60*24*6, 1000):
    for i in range(t, t + 1000):
        insert_reading(ds, 50 * math.sin(i*math.pi/(86400)), i)
    time.sleep(1)

print 'Done'
