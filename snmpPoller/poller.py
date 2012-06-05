#!/usr/bin/python
import os,sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(BASE_DIR + "/../")
print BASE_DIR
sys.path.insert(0,BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'settings')
import netsnmp
from datetime import datetime
from django.utils.timezone import now
from snmpPoller.models import *


url = "http://192.168.11.19:8080/collector/add_reading/"
authToken = "correcthorsebatterystaple"


streams = SnmpStream.objects.filter(active=True)

for s in streams:
    print "Polling %s oid=%s" % (s.host.hostname,s.oid)
    var = netsnmp.Varbind(s.oid)
    res = netsnmp.snmpget(var,Version=s.host.version,DestHost=s.host.hostname,Community=s.host.community)
    if(res):
        value = int(res[0])
        print "Got Value %d" % (value)
        
        if(s.lastTime == 0 or s.lastTime == None):
            s.lastTime = now()
            s.lastValue = value
            s.save()
        
        else:
            timediff = now() - s.lastTime
            timediff = timediff.seconds
        
            #check if the differen in time was to long
            if(timediff > s.maxTime):
                s.lastTime = now()
                s.lastValue = value
                s.save()
                
            else:

                valdiff = value - s.lastValue
                #If we rollover
                if(valdiff < 0):
                    valdiff += s.maxValue 
        
                s.lastTime = now()
                s.lastValue = value
                s.save()

                #cannot divide by zero
                if(timediff != 0):
                    rate = float(valdiff) / float(timediff)
                else:
                    rate = 0.0;
                
                if(rate > s.maxValPerPoll):
                    print "Possible Spike"

                else:
                    print "Rate is %f timediff=%d valdiff=%d" % (rate,timediff,valdiff)
                    command = "curl \"" + url + "?auth_token=" + authToken + "&datastream_id=" + str(s.dataStream.id) + "&value=" + str(rate) + "\""   
                    print os.system(command)

    else:
        print "no data for host"
    
    print ""
