#System Imports
from django.template import RequestContext, Context
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.decorators.http import require_GET
try: import simplejson as json
except ImportError: import json

#Local Imports
from portcullis.models import DataStream, SensorReading, PortcullisUser, ScalingFunction, Key
from check_access import check_access
from graphs.data_reduction import reduceData, reductFunc
from graphs.models import SavedDSGraph

@require_GET
def display_graphs(request):
    '''
    ' Use JSON data to retrieve the appropriate datastreams for rendering.
    '''

    # TODO: Figure out how we want to do check_access
    #response = check_access(request)
    #if(response):
    #    return response

    json_data = json.loads(request.GET['json_data'])

    streams = DataStream.objects.filter(id__in = json_data['streams'])

    t_graph_contain = loader.get_template('graph_container.html')
    c_graph_contain = RequestContext(request, {'graphs':graphs_list(streams)})
        
    return HttpResponse(t_graph_contain.render(c_graph_contain), mimetype="text/html")

def graphs_list(streams):
    '''
    ' Take an iterable of graph streams and return a list of rendered graph objects.
    ' 
    ' Keyword args:
    '  streams - An iterable of DataStreams.
    '''
    reductions = reductFunc.keys()    
    graphs = []
    t_graph = loader.get_template('graph.html')
    for stream in streams:
        c_graph = Context({
                'id': stream.id,
                'node_id': stream.node_id,
                'port_id': stream.port_id,
                'reductions': reductions
                })
        graphs.append(t_graph.render(c_graph))
    return graphs


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
                'ds_label':            ds,
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
        "ds_label":            ds.name,
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

