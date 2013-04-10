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


def get_data_by_ds_column(request):
    '''
    ' This view will take a column name/value and a time range (in epoch secs),
    ' and return a json response containing all the matching sensor data points.
    '
    ' returns - HttpResponse containing jsondata {<ds_id>: [(<timestamp>, <value>), ...], ... }
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

    data_points = SensorReading.objects.select_related().filter(
        timestamp__gte=time_start,
        timestamp__lte=time_end
        ).extra(
        where=['portcullis_sensorreading.datastream_id IN (' +
               'SELECT portcullis_datastream.id ' +
               'FROM portcullis_datastream ' +
               'WHERE portcullis_datastream.' + column + ' LIKE %s )'],
        params=['%' + value + '%'])

    # Echo back query
    data = {
        'column': column,
        'value': value,
        'start': time_start,
        'end': time_end
        }

    # Get the datastreams that we are interested.
    datastream_ids = data_points.order_by('datastream').distinct('datastream').values_list('datastream', flat=True)

    for id in datastream_ids:
        points = data_points.filter(datastream=id).values_list('timestamp', 'value')
        data[id] = [(x[0], float(x[1])) for x in points]

    print 'Took: %f seconds' % (time.time() - beg_time)
    return HttpResponse(json.dumps(data), mimetype='application/json')
