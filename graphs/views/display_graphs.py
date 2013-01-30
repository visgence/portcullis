#System Imports
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
try: import simplejson as json
except ImportError: import json

#Local Imports
from portcullis.models import DataStream, SensorReading, PortcullisUser, ScalingFunction, Key
from check_access import check_access
from graphs.data_reduction import reduceData, reductFunc
from graphs.models import SavedDSGraph

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

            graphs_page = loader.get_template('display_nodes.html')
            graphs_c = RequestContext(request, data)
        
            controls_page = loader.get_template('graph_controls.html')
            controls_c = RequestContext(request, data)

            template_data = {'graphs': graphs_page.render(graphs_c),
                             'controls': controls_page.render(controls_c)}
            return HttpResponse(json.dumps(template_data),mimetype="application/json")

        #If we have a node or node/port pair then pull streams for those otherwise pull streams
        if(node != None and port != None):
           data['streams'] = DataStream.objects.filter(node_id = int(node), port_id = int(port), can_read__owner = request.user)
        elif(node != None):
            data['streams'] = DataStream.objects.filter(node_id = int(node), can_read__owner = request.user)
        else:
            data['streams'] = DataStream.objects.filter(can_read__owner = request.user)
      
        graphs_page = loader.get_template('display_nodes.html')
        graphs_c = RequestContext(request, data)

        controls_page = loader.get_template('graph_controls.html')
        controls_c = RequestContext(request, data)

        
        template_data = {'graphs': graphs_page.render(graphs_c),
                         'controls': controls_page.render(controls_c)}
        return json.dumps(template_data)
        #return render(request,'display_nodes.html', data, context_instance=RequestContext(request))        


def render_graph(request):
    '''
    Takes a single datastream id and a time frame and generates json for the data.
    '''
    jsonData = request.REQUEST.get('json_data', None)
    if jsonData is None:
        raise Http404

    try:
        portcullisUser = request.user.portcullisuser
    except ObjectDoesNotExist:
        portcullisUser = None

    return HttpResponse(getStreamData(json.loads(jsonData), portcullisUser), mimetype="application/json")

def shared_graph(request, token, id):
    '''
    This function will use a key to send the jsonData for a shared graph.
    '''

    try:
        # Get the key from the token
        key = Key.objects.get(key = token)

        # Get the graph from the id.
        graph = SavedDSGraph.objects.get(id = id)
    except ObjectDoesNotExist:
        raise Http404('Graph %s/%s/ does not exist' % (token, str(id)))
        
    params = {
        'start':         graph.start,
        'end':           graph.end,
        'reduction':     graph.reduction_type,
        'granularity':   graph.granularity,
        'datastream_id': graph.datastream.id
        }
    return HttpResponse(getStreamData(params, key), mimetype="application/json")
    

def getStreamData(g_params, auth):
    '''
    ' This function will return streamData serialized to JSON for graphing.
    '
    ' g_params - A dictionary containing all the necessary information to get the stream data
    '            for graphing.
    '            Required keys:
    '                start, end, ds_id, granularity
    ' auth     - Used for authentication.  This can either be a portcullis user or a key
    '''

    start = g_params['start']
    end = g_params['end']
    ds_id = g_params['datastream_id']
    granularity = int(g_params['granularity'])
    reduction_type = g_params['reduction']

    
    ds = DataStream.objects.get_ds_and_validate(ds_id, auth, 'read')
    
    if not isinstance(ds, DataStream):
        print 'User verification failed: ' + ds
        stream_data = {'data':[],
                'permission':       False,
                'label':            ds,
                "datastream_id":    ds_id,
                }
        return json.dumps(stream_data)
    
    #Pull the data for this stream
    #Check if there are less points in timeframe then granularity
    readings = SensorReading.objects.filter(timestamp__gte = start, timestamp__lte = end,
                                            datastream = ds).order_by('timestamp')
    numReadings = readings.count()

    # if we have less readings than our granularity, put them in a list, otherwise reduce it
    if(numReadings <= granularity):
        data_points = [ [x.timestamp,float(x.value)] for x in readings ]
    else:
        data_points = reduceData(list(readings.values_list('timestamp', 'value')), granularity, reduction_type)


    min_value = ds.min_value
    if(min_value != None):
        min_value = float(min_value)

    max_value = ds.max_value
    if(max_value != None):
        max_value = float(max_value)

    stream_data = {
        "label":            ds.name,
        "port_id":          ds.port_id,
        "data":             data_points,
        "num_readings":     numReadings,
        "max_value":        max_value,
        "min_value":        min_value,
        "description":      ds.description,
        "scaling_function": ds.scaling_function.id,
        "datastream_id":    ds.id,
        "color":            ds.color,
        "shadowSize":       0,
        "points":           { "show": False },
        "node_id":          ds.node_id,
        "units":            ds.units,
        "permission":       True
        }


    return json.dumps(stream_data)

