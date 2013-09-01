#!/usr/bin/python
import os,sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(BASE_DIR)
print BASE_DIR
sys.path.insert(0,BASE_DIR)
import netsnmp
import time
import ordereddict
import pickle
import json
import requests
urlCreate = "http://192.168.11.19:8003/api/createSensors/"
urlAdd = "http://192.168.11.19:8003/api/addList/"
filename = 'streams.pickle'
STREAMS = None

class Stream():
    
    lastTime = None
    lastValue = None
    maxValue = None
    maxValPerPoll = 0
    maxTime = None
    value =None
    oid = ''
    host = ''
    tag = None
    index = None
    iid = None
    ifname = None

    def __init__(self,maxValue=2**32,maxValPerPoll=125000000,maxTime=120,host='',oid='',iid=None,tag=None,value=None,ifName=None):
        self.maxValue = maxValue
        self.maxValPerPoll = maxValPerPoll
        self.maxTime = maxTime
        self.host = host
        self.oid = oid
        self.iid = iid
        self.tag = tag
        self.value = value
        self.index = oid + "-" + host
        self.ifName = ifName

    def save(self,streams):
        #Check if OID is in global Streams
   
        
        if self.index in streams:
            #Just update the value of that stream
            if self.index is not None:
                streams[self.index].value = self.value
            if self.lastTime is not None:
                streams[self.index].lastTime = self.lastTime
            if self.lastValue is not None:
                streams[self.index].lastValue = self.lastValue
            if self.maxValue is not None:
                streams[self.index].maxValue = self.maxValue
            if self.maxValPerPoll is not None:
                streams[self.index].maxValPerPoll = self.maxValPerPoll
            if self.maxTime is not None:
                streams[self.index].maxTime = self.maxTime
            if self.ifName is not None:
                streams[self.index].ifName = self.ifName
        
        else:
            #Add This stream to the dictonary 
            streams[self.index] = self

def main():
    
    streams = ordereddict.OrderedDict({})
    #streams = {}
    
    
    try:
        FILE = open(filename,'r')
        streams= pickle.load(FILE)
        print "Loaded File"
        print streams
    except:
        "No File, creating"


    print "Streams Read"
  
    hosts = ['192.168.11.200','192.168.11.1']
    snmpTypes = ['ifInOctets','ifOutOctets','ifInUcastPkts','ifOutUcastPkts']

    for hostname in hosts:
        snmpHost = {'Community': 'public', 'DestHost': hostname, 'Version': 2}
        oid = netsnmp.VarList(netsnmp.Varbind('ifTable'))
        netsnmp.snmpwalk(oid,**snmpHost)
       
        ifNames = {} 
        for o in oid:
        
            if(o.tag == "ifDescr"):
                ifNames[o.iid] = o.val

            if(o.tag in snmpTypes):
                s =Stream(oid="%s.%s"%(o.tag,o.iid),
                        iid=o.iid,
                        tag=o.tag,
                        value=int(o.val),
                        host=hostname,
                        ifName=ifNames[o.iid])
                s.save(streams)

    #createStreams(streams)
    #print STREAMS
    results = processStreams(streams)
    print results
    postResults(results)
    try:
        FILE.close()
    except:
        pass

    f = open(filename,'w')
    pickle.dump(streams,f)
    f.close()


def createStreams(streams):

    jsonData = {"sensors":[],"email":"auth@example.com"}

    for s in streams.values():
        sensor ={}
        sensor['uuid'] = s.index
        sensor['name'] = "%s|%s|%s" % (s.host,s.tag,s.ifName)
        jsonData['sensors'].append(sensor)
           
    
    data = json.dumps(jsonData,indent=4)
    r = requests.post(urlCreate,data=data)
    print r.text

def postResults(results):
    
    jsonData = []
    for r in results:
        jsonData.append([r['index'],r['value']])
    
    data = json.dumps(jsonData,indent=4)
    r = requests.post(urlAdd,data=data)
    print r.text

def processStreams(streams):
    streamList = streams.values()

    results = []

    for s in streamList:
        print "Polling %s oid=%s" % (s.host,s.oid)
        res = s.value
        if(res):
            value = int(res)
            print "Got Value %d" % (value)
            
            if(s.lastTime == 0 or s.lastTime == None):
                s.lastTime = int(time.time())
                s.lastValue = value
                s.save(streams)
            
            else:
                timediff = int(time.time()) - s.lastTime
                timediff = timediff
            
                #check if the differen in time was to long
                if(timediff > s.maxTime):
                    s.lastTime = int(time.time())
                    s.lastValue = value
                    s.save(streams)
                    
                else:

                    valdiff = value - s.lastValue
                    #If we rollover
                    if(valdiff < 0):
                        valdiff += s.maxValue 
            
                    s.lastTime = int(time.time())
                    s.lastValue = value
                    s.save(streams)

                    #cannot divide by zero
                    if(timediff != 0):
                        rate = float(valdiff) / float(timediff)
                    else:
                        rate = 0.0;
                    
                    if(rate > s.maxValPerPoll):
                        print "Possible Spike"

                    else:
                        print "Rate is %f timediff=%d valdiff=%d" % (rate,timediff,valdiff)
                        results.append({'index':s.index,'value':rate})
                        #command = "curl \"" + url + "?auth_token=" + authToken + "&datastream_id=" + str(s.dataStream.id) + "&value=" + str(rate) + "\""   
                        #print os.system(command)

        else:
            print "no data for host"
        
        print ""
    return results

if __name__ == "__main__":
    main()
