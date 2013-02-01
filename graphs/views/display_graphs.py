#System Imports
from django.template import RequestContext
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

    data = {
        'granularity': json_data.get('granularity', ''),
        'start': json_data.get('start', ''),
        'end': json_data.get('end', ''),
        'streams': DataStream.objects.filter(id__in = json_data['streams']),
        'reductions': reductFunc.keys()
        }    
    if(data['granularity'] != ''):
        data['granularity'] = int(data['granularity'])
        
    graphs_page = loader.get_template('display_nodes.html')
    graphs_c = RequestContext(request, data)
        
    controls_page = loader.get_template('graph_controls.html')
    controls_c = RequestContext(request, data)
        
    template_data = {'graphs': graphs_page.render(graphs_c),
                         'controls': controls_page.render(controls_c)}
    return HttpResponse(json.dumps(template_data),mimetype="application/json")

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

