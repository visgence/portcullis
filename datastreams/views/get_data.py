'''
' datastreams/views/get_data.py
' Contributing Authors:
'    Jeremiah Davis (Visgence, Inc)
'
' (c) 2013 Visgence, Inc.
'''

# System imports
from django.http import HttpResponse
from django.template import RequestContext, loader
try:
    import simplejson as json
except ImportError:
    import json


# Local imports
from portcullis.models import DataStream, SensorReading
from portcullis.utils import DecimalEncoder


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
        error = 'Error: No jsonData received.'
        return HttpResponse(json.dumps({'errors': error}), mimetype='application/json')
    try:
        jsonData = json.loads(jsonData)
    except Exception as e:
        error = 'Error: Invalid JSON: ' + str(e)
        return HttpResponse(json.dumps({'errors': error}, mimetype='application/json'))

    try:
        column = jsonData['column']
        value = jsonData['value']
        time_start = jsonData['start']
        time_end = jsonData['end']
    except KeyError as e:
        error = 'Error: KeyError: ' + str(e)
        return HttpResponse(json.dumps({'errors': error}, mimetype='application/json'))

    # Scrub column, so it is safe to use in query
    ds_columns = [x.get_attname_column()[1] for x in DataStream._meta.fields]

    if column not in ds_columns:
        error = 'Error: Column Name %s not in DataStream table.' % column
        return HttpResponse(json.dumps({'errors': error}, mimetype='application/json'))

    data_points = list(SensorReading.objects.select_related().filter(
        timestamp__gte=time_start,
        timestamp__lte=time_end
        ).extra(
        where=['portcullis_sensorreading.datastream_id IN (' +
               'SELECT portcullis_datastream.id ' +
               'FROM portcullis_datastream ' +
               'WHERE portcullis_datastream.' + column + ' LIKE %s )'],
        params=['%' + value + '%']).values_list('datastream', 'value', 'timestamp'))

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

    return_data = json.dumps(data, cls=DecimalEncoder)
    return HttpResponse(json.dumps(data, cls=DecimalEncoder), mimetype='application/json')
