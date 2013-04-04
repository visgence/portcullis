#System Imports
from django.template import RequestContext, Context
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.decorators.http import require_GET
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from portcullis.models import DataStream, SensorReading, ScalingFunction, Key
from check_access import check_access
from graphs.data_reduction import reduceData, reductFunc
from graphs.models import SavedDSGraph


def display_simple_base(request):

    start = request.GET['start']
    end = request.GET['end']
    streams = request.GET['streams']
    
    t = loader.get_template('base_simple.html')
    c = RequestContext(request, {
        'start': start, 
        'end': end,
        'streams': streams
    })
    return HttpResponse(t.render(c), mimetype='text/html')

def display_simple_graph(request):
    
    json_data = json.loads(request.GET['json_data'])

    try:
        stream = DataStream.objects.get(id = int(json_data['stream']))
    except ObjectDoesNotExist as e:
        raise Http404()

    reductions = reductFunc.keys()    
    t_graph = loader.get_template('graph.html')
    c_graph = Context({
        'id': stream.id,
        'reduction': stream.reduction_type,
        'reductions': reductions
    })

    return HttpResponse(t_graph.render(c_graph), mimetype="text/html")

@require_GET
def display_graph(request):
    '''
    ' Use JSON data to retrieve the appropriate datastream for rendering.
    '''
    
    user = check_access(request)
    if isinstance(user, HttpResponse):
        return user.content
    
    json_data = json.loads(request.GET['json_data'])

    try:
        stream = DataStream.objects.get(id = int(json_data['stream']))
        if not stream.can_view(user):
            raise Http404("Sorry, but you do not have permission to view this graph.")
    except ObjectDoesNotExist as e:
        raise Http404()

    reductions = reductFunc.keys()    
    t_graph = loader.get_template('graph.html')
    c_graph = Context({
        'id': stream.id,
        'reduction': stream.reduction_type,
        'reductions': reductions
    })

    return HttpResponse(t_graph.render(c_graph), mimetype="text/html")


def render_graph_container(request):
    '''
    ' Renders and returns just the graph container as html.
    '''

    t_graph_contain = loader.get_template('graph_container.html')
    c_graph_contain = RequestContext(request, {})
    return HttpResponse(t_graph_contain.render(c_graph_contain), mimetype="text/html")

def render_graph(request):
    '''
    Takes a single datastream id and a time frame and generates json for the data.
    '''
    jsonData = request.REQUEST.get('json_data', None)
    if jsonData is None:
        raise Http404

    return HttpResponse(getStreamData(json.loads(jsonData), request.user), mimetype="application/json")

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
        'datastream_id': graph.datastream.id,
        'zoom_start':    graph.zoom_start,
        'zoom_end':      graph.zoom_end
        }
    return HttpResponse(getStreamData(params, key, request.user), mimetype="application/json")
    

def getStreamData(g_params, auth, user = None):
    '''
    ' This function will return streamData serialized to JSON for graphing.
    '
    ' g_params - A dictionary containing all the necessary information to get the stream data
    '            for graphing.
    '            Required keys:
    '                start, end, ds_id, granularity
    ' auth     - Used for authentication.  This can either be a portcullis user or a key
    ' user     - Secondary authentication.  should only be a request.user.  May change in future...
    '''
    start = g_params['start']
    end = g_params['end']
    ds_id = g_params['datastream_id']
    granularity = int(g_params['granularity'])
    reduction_type = g_params['reduction']
    zoom_start = None
    zoom_end = None

    if 'zoom_start' in g_params:
        zoom_start = g_params['zoom_start']
    if 'zoom_end' in g_params:
        zoom_end = g_params['zoom_end']

    
    ds = DataStream.objects.get_ds_and_validate(ds_id, auth, 'read')
    
    if not isinstance(ds, DataStream):
        # Try auth2
        try:
            ds = DataStream.objects.get_ds_and_validate(ds_id, user, 'read')
        except AttributeError:
            ds = None
        if not isinstance(ds, DataStream):
            print 'User verification failed: ' + ds
            stream_data = {
                'data':                [],
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
        "granularity":      granularity,
        "ds_label":         ds.name,
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
        "units":            ds.units,
        "permission":       True,
        "xmax":             end,
        "xmin":             start,
        "zoom_start":       zoom_start,
        "zoom_end":         zoom_end
        }


    return json.dumps(stream_data)

