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
from portcullis.models import DataStream, SensorReading, PortcullisUser, ScalingFunction
from check_access import check_access
from graphs.data_reduction import reduceData, reductFunc

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
        if 'json_data' in request.GET:
            json_data = json.loads(request.GET['json_data'])
            view_streams = json_data.get('view', [])
            owned_streams = json_data.get('owned', [])
            public_streams = json_data.get('public', [])
        else:
            json_data = request.GET
            view_streams = json_data.getlist('view', [])
            owned_streams = json_data.getlist('owned', [])
            public_streams = json_data.getlist('public', [])
        
        node = json_data.get('node', '')
        port = json_data.get('port', '')
        start = json_data.get('start', '')
        end = json_data.get('end', '')
        granularity = json_data.get('granularity', '')
        show_public= json_data.get('show_public', '')

        data = {
            'granularity':granularity,
            'start':start,
            'end':end,
            'streams':DataStream.objects.none(),
            'reductions': reductFunc.keys()
        }
        
        if(granularity != ''):
            data['granularity'] = int(granularity)
        
        #Grab all read-able streams
        if(len(view_streams) > 0):
            for stream in view_streams:
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        #Grab all owned streams by this user
        if(len(owned_streams) > 0):
            for stream in owned_streams:
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        #Grab all public streams
        if(len(public_streams) > 0):
            for stream in public_streams:
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        #It's possible for this to be empty so check then order the streams and return them
        if(data['streams']):
            data['streams'] = data['streams'].order_by('node_id', 'port_id', 'id')

            if 'json_data' not in request.GET: 
                return render(request,'display_nodes_shared.html', data, context_instance=RequestContext(request))        

            t = loader.get_template('display_nodes.html')
            c = RequestContext(request, data)
            return HttpResponse(json.dumps(t.render(c)),mimetype="application/json")

        #If we have a node or node/port pair then pull streams for those otherwise pull streams
        if(node != None and port != None):
           data['streams'] = DataStream.objects.filter(node_id = int(node), port_id = int(port), can_read__owner = request.user)
        elif(node != None):
            data['streams'] = DataStream.objects.filter(node_id = int(node), can_read__owner = request.user)
        else:
            data['streams'] = DataStream.objects.filter(can_read__owner = request.user)
      
        t = loader.get_template('display_nodes.html')
        c = RequestContext(request, data)
        return json.dumps(t.render(c))
        #return render(request,'display_nodes.html', data, context_instance=RequestContext(request))        


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

        reduction_type = request.GET.get('reduction', 'mean')
        if reduction_type is None or reduction_type == '':
            reduction_type = 'mean'

        try:
            portcullisUser = request.user.portcullisuser
        except ObjectDoesNotExist:
            portcullisUser = None

        # Get DataStream if it exists and we have permission
        stream_info = DataStream.objects.get_ds_and_validate(datastream_id, portcullisUser, 'read')

        if not isinstance(stream_info, DataStream):
            print 'User verification failed: ' + stream_info
            data = {'data':[],
                    'permission':       False,
                    'label':            stream_info,
                    "datastream_id":    datastream_id,
                    }
            return HttpResponse(json.dumps(data), mimetype='application/json')                  

        stream_info.permission = "true"

        #These fields could be used for graph settings client-side
        stream_info.xmin = start
        stream_info.xmax = end


        #Pull the data for this stream
        #Check if there are less points in timeframe then granularity
        readings = SensorReading.objects.filter(timestamp__gte = start, timestamp__lte = end, datastream = datastream_id).order_by('timestamp')
        numReadings = readings.count()

        if(numReadings < granularity):
            #loop through and add all points to data
            data = [ [x.timestamp,float(x.value)] for x in readings ]

        else:
            data = reduceData(list(readings.values_list('timestamp', 'value')), granularity, reduction_type)

        stream_info.num_readings = numReadings
        stream_info.data = data
        json_data = to_json(stream_info)

        return HttpResponse(json_data, mimetype='application/json')

        
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
                   "port_id":stream.port_id,
                   "data":stream.data,
                   "num_readings":stream.num_readings,
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
                   "permission":True
                   }


    return json.dumps(stream_data)

