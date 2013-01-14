#System Imports
from django.template import RequestContext
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
import json

#Local Imports
from portcullis.models import DataStream, SensorReading, ScalingFunction 
from check_access import check_access
from data_reduction import reduceData

def display_graphs(request):
    '''
    Grabs all relevent data streams that are to be displayed and returns them to the display_nodes
    template. There are two ways for this to be called. The first is through the user portal after
    logging in.  This requires them to check off all streams they want to see and we grab them. 
    Otherwise we get url parameters through a GET and obtain the proper streams that way.

    TODO: The share this view linkage needs GET in order to work.  Would like to seperate that 
          functionality out to have POST as well from the user portal perhaps.  
    '''

    response = check_access(request)
    if(response):
        return response

    if(request.method == 'GET'):
        node = request.GET.get('node')
        port = request.GET.get('port')
        start = request.GET.get('start')
        end = request.GET.get('end')
        granularity = request.GET.get('granularity')
        show_public= request.GET.get('show_public')

        data = {
                    'granularity':granularity,
                    'start':start,
                    'end':end,
                    'streams':DataStream.objects.none(),
               }
        
        if(granularity != None):
            data['granularity'] = int(granularity)

        #Grab all read-able streams
        if(request.GET.getlist('view')):
            for stream in request.GET.getlist('view'):
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        #Grab all owned streams by this user
        if(request.GET.getlist('owned')):
            for stream in request.GET.getlist('owned'):
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        #Grab all public streams
        if(request.GET.getlist('public')):
            for stream in request.GET.getlist('public'):
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        #TODO: Pull shared streams if the user requested them

        #It's possible for this to be empty so check then order the streams and return them
        if(data['streams']):
            data['streams'] = data['streams'].order_by('node_id', 'port_id', 'id')
            return render(request,'display_nodes.html', data, context_instance=RequestContext(request))        

        #If we have a node or node/port pair then pull streams for those otherwise pull streams
        if(node != None and port != None):
           data['streams'] = DataStream.objects.filter(node_id = int(node), port_id = int(port), users = request.user)
        elif(node != None):
            data['streams'] = DataStream.objects.filter(node_id = int(node), users = request.user)
        else:
            data['streams'] = DataStream.objects.filter(users = request.user)

        return render(request,'display_nodes.html', data, context_instance=RequestContext(request))        


def render_graph(request):
    '''
    Takes a single datastream id and a time frame and generates json for the data.
    '''

    if(request.method == 'GET'):
        start = int(request.GET.get('start'))
        end = int(request.GET.get('end'))
        datastream_id = int(request.GET.get('datastream_id'))
        granularity = int(request.GET.get('granularity'))
        total_time = end - start
        stream_data = []

        if(granularity == None):
            granularity = 300
   
        #Pull the data for this stream
        stream_info = DataStream.objects.get(id = datastream_id)

        #These fields could be used for graph settings client-side
        stream_info.xmin = start
        stream_info.xmax = end

        #Check for read and public permissions.  Set a flag, true or false.
        try:
            if(stream_info.is_public == True or stream_info.userpermission_set.get(read = True, user = request.user)):
                stream_info.permission = "true"
        except ObjectDoesNotExist:
            stream_info.data = []
            stream_info.permission = "false"
            json = to_json(stream_info)
            return HttpResponse(json)

        #Check if there are less points in timeframe then granularity
        readings = SensorReading.objects.filter(date_entered__gte = start, date_entered__lte = end, datastream = datastream_id).order_by('date_entered')
        numReadings = readings.count()

        if(numReadings < granularity):
            #loop through and add all points to data
            data = [ [x[0],float(x[1])] for x in readings ]

        else:
            data = reduceData(list(readings.values_list('date_entered', 'sensor_value')), granularity, 'mean')
            #increment = numReadings/granularity
            #rawData = list(readings.values_list('date_entered', 'sensor_value'))
            '''
            aveTime = np.convolve([t[0] for t in rawData], np.ones(increment)/float(increment), 'same')
            aveData = np.convolve([float(x[1]) for x in rawData], np.ones(increment)/float(increment),'same')
            for i in range(0, numReadings, increment):
                data.append([aveTime[i], aveData[i]])

            del(data[-1])
            del(data[0])
            '''
            #for i in range(0, numReadings, increment):
                #data.append(data_reduction.reduce_data(rawData[i:i+increment]))
                #data.append([rawData[i][0], float(rawData[i][1])])
                

        stream_info.data = data
        json = to_json(stream_info)

        return HttpResponse(json)

        
def to_json(stream):
    '''
    Takes a single stream and turns all of it's data into json and returns it.
    '''

    min_value = stream.min_value
    if(min_value != None):
        min_value = float(min_value)

    max_value = stream.max_value
    if(max_value != None):
        max_value = float(max_value)



    stream_data = {"reduction_type":stream.reduction_type,
                   "label":stream.name,
                   "port_id":int(stream.port_id),
                   "data":stream.data,
                   "max_value":max_value,
                   "min_value":min_value,
                   "description":stream.description,
                   "scaling_function":stream.scaling_function.id,
                   "datastream_id":stream.id,
                   "color":stream.color,
                   "node_id":int(stream.node_id),
                   "xmin":stream.xmin,
                   "xmax":stream.xmax,
                   "units":stream.units,
                   "permission":stream.permission}

    return json.dumps(stream_data)

