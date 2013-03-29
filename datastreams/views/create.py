"""
" datastreams/views/create.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#System Imports
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from portcullis.models import DataStream, Key, ScalingFunction


@require_POST
@csrf_exempt
def createDs(request):
    '''
    ' Creates a DataStream with data from json and with the owner of the specified token.
    '
    ' The json required format is the following:
    '   {
    '       "token"  : key token,
    '       "ds_data": Dictionary of key value pairs. Keys are names that match datastream field names and
    '                  value is the value to set to the new object.
    '   }
    '
    ' This json is then given to a dictionary to be sent as the request like so:
    '   { "jsonData": json_stuff }
    '
    ' Returns: HttpResponse with Json containing the new DataStreams id or error is anything went wrong.
    '''

    #TODO: for now screw permissions, but later, put them in!!

    try:
        json_data = json.loads(request.POST.get("jsonData"))
    except Exception as e:
        return get_http_response("From createDs: Problem getting json data from request.", str(e))

    try:
        key = Key.objects.get(key=json_data['token'])
    except Key.DoesNotExist as e:
        return get_http_response("From createDs: Key with token '%s' does not exist." % str(json_data['token']), str(e))
    except KeyError as e:
        return get_http_response("From createDs: 'token' does not exist in the json data.", str(e))

    try:
        ds_name = json_data['ds_data']['name']
    except Exception as e:
        return get_http_response("From createDs: Exception getting DS name: %s." % type(e), str(e))

    try:
        ds = DataStream.objects.get(name=ds_name, owner=key.owner)
    except DataStream.DoesNotExist:
        ds = DataStream(owner=key.owner)
        for attr, val in json_data['ds_data'].iteritems():
            if attr == "scaling_function":
                try:
                    sc = ScalingFunction.objects.get(name=val)
                except ScalingFunction.DoesNotExist as e:
                    return get_http_response("From createDs: scaling function with name '%s' does not exist." % str(val), str(e))
                setattr(ds, attr, sc)
            else:
                try:
                    setattr(ds, attr, val)
                except Exception as e:
                    error = "From createDs: There was a problem setting '%s' with the value '%s'." % (str(attr), str(val))
                    return get_http_response(error, str(e))
        try:
            ds.full_clean()
            ds.save()
        except ValidationError as e:
            return get_http_response("From createDs: There were one or more problems setting DataStream attributes.", str(e))

    return_data = {'id': ds.pk}
    ds.can_read.add(key)
    ds.can_post.add(key)

    return HttpResponse(json.dumps(return_data), mimetype="application/json")


def get_http_response(msg, e):
    '''
    ' Helper method for createDs that returns a HttpResponse with dumped json containing an error message
    ' and an exception.
    '
    ' Keyword Arguments:
    '   msg - String error message.
    '   e   - String exception that was caught.
    '
    ' Return: HttpResonse object containing json for errors and exceptions.
    '''

    return_data = {
        'error':     msg,
        'exception': e
    }

    return HttpResponse(json.dumps(return_data), mimetype="application/json")
