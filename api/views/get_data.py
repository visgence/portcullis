'''
' api/views/get_data.py
' Contributing Authors:
'    Jeremiah Davis (Visgence, Inc)
'
' (c) 2013 Visgence, Inc.
'''

# System imports
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
try:
    import simplejson as json
except ImportError:
    import json


# Local imports
from graphs.models import DataStream, SensorReading
from portcullis.utils import DecimalEncoder
from graphs.data_reduction import reduceData
from api.utilities import cors_http_response_json


def get_data_by_ds_column(request):
    '''
    ' This view will take a column name/value and a time range (in epoch secs),
    ' and return a json response containing all the matching sensor data points.
    '
    ' returns - HttpResponse containing jsondata {'echo of query', 'streams': [[<ds_id>, <value>, <timestamp>]] }
    '''
    # TODO: Check perms, etc.
    import time
    beg_time = time.time()
    jsonData = request.REQUEST.get('jsonData', None)
    if jsonData is None:
        return cors_http_response_json({'errors': 'Error: No jsonData received.'})

    try:
        jsonData = json.loads(jsonData)
    except Exception as e:
        return cors_http_response_json({'errors': 'Error: Invalid JSON: ' + str(e)})

    try:
        column = jsonData['column']
        value = jsonData['value']
        time_start = jsonData['start']
        time_end = jsonData['end']
    except KeyError as e:
        return cors_http_response_json({'errors': 'Error: KeyError: ' + str(e)})

    # Scrub column, so it is safe to use in query
    ds_columns = [x.get_attname_column()[1] for x in DataStream._meta.fields]

    if column not in ds_columns:
        return cors_http_response_json({'errors': 'Error: Column Name %s not in DataStream table.' % column})

    kwargs = {
        'timestamp__gte':                   time_start,
        'timestamp__lte':                   time_end,
        'datastream__'+column+'__contains': value
    }

    data_points = list(SensorReading.objects.select_related().filter(**kwargs).values_list('datastream', 'value', 'timestamp'))

    elapsed_time = time.time() - beg_time
    print 'Took: %f seconds before JSON' % elapsed_time
    # Echo back query, and send data
    data = {
        'column':  column,
        'value':   value,
        'start':   time_start,
        'end':     time_end,
        'streams': data_points,
        'time':    elapsed_time
        }

    resp = HttpResponse(json.dumps(data, cls=DecimalEncoder), mimetype='application/json')
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def render_graph(request):
    '''
    Takes a single datastream id and a time frame and generates json for the data.
    '''
    jsonData = request.REQUEST.get('json_data', None)
    if jsonData is None:
        return cors_http_response_json({'error': "Unrecognized data."})

    return cors_http_response_json(get_stream_data(json.loads(jsonData), request.user))


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
        return cors_http_response_json({'error': 'Graph %s/%s/ does not exist' % (token, str(id))})
    
    params = {
        'start':         graph.start,
        'end':           graph.end,
        'reduction':     graph.reduction_type,
        'granularity':   graph.granularity,
        'datastream_id': graph.datastream.id,
        'zoom_start':    graph.zoom_start,
        'zoom_end':      graph.zoom_end
        }
    
    return cors_http_response_json(get_stream_data(params, key, request.user))


def get_stream_data(g_params, auth, user = None):
    '''
    ' This function will return streamData for graphing
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
    try:
        reduction_type = g_params['reduction']
    except:
        reduction_type = 'mean'
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
            return stream_data
    
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


    return stream_data

