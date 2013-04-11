"""
" datastreams/views/create.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"    Jerry Davis (Visgence, Inc)
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

from django.db import transaction

#Local Imports
from portcullis.models import DataStream, Key, ScalingFunction


@require_POST
@csrf_exempt
@transaction.commit_manually
def createDs(request):
    '''
    ' Creates DataStreams with an array of data from json and with the owner of the specified token.
    '
    ' The json required format is the following:
    '   [{
    '       "token"  : key token,
    '       "ds_data": Dictionary of key value pairs. Keys are names that match datastream field names and
    '                  value is the value to set to the new object.
    '   }, etc]
    '
    ' This json is then given to a dictionary to be sent as the request like so:
    '   { "jsonData": json_stuff }
    '
    ' Returns: HttpResponse with Json containing a list with the new DataStream's ids or error is anything went wrong.
    '''

    #TODO: for now screw permissions, but later, put them in!!
    
    try:
        json_data = json.loads(request.POST.get("jsonData"))
    except Exception as e:
        transaction.rollback()
        return get_http_response("From createDs: Problem getting json data from request.", str(e))
    
    #jsonData should contain a list of data.
    if not isinstance(json_data, list):
        transaction.rollback()
        return get_http_response("From createDs: json data is not a list.", '')

    errors = {}
    return_ids = {}
    for data in json_data:
        
        try:
            key = Key.objects.get(key=data['token'])
        except Key.DoesNotExist as e:
            error = "From createDs: Key with token '%s' does not exist." % str(data['token'])
            errors.append({"error": error, "exception": str(e)})
            continue
        except KeyError as e:
            errors.append({"error": "'token' does not exist in the json data.", "exception": str(e)})
            continue
        
        try:
            ds_name = data['ds_data']['name']
        except Exception as e:
            error = "From createDs: Exception getting DS name: %s." % type(e) 
            errors.append({"error": error, "exception": str(e)})
            continue
        
        try:
            ds = DataStream.objects.get(name=ds_name, owner=key.owner)
        except DataStream.DoesNotExist:
            ds = create_ds(key, data) 

            #If not a ds then an error
            if not isinstance(ds, DataStream):
                errors[ds_name] = ds
                continue

        return_ids[ds_name] = ds.pk
        ds.can_read.add(key)
        ds.can_post.add(key)

    transaction.commit()
    return HttpResponse(json.dumps({'ids': return_ids, "errors": errors}), mimetype="application/json")


def create_ds(key, data):
    '''
    ' Creates a new Datastream given a key and some data.  The keys owner is used as the Datastream's owner.
    ' The data needs to contain the name for the Datastream as a minimum in order to create it.
    '
    ' Keyword Arguments: 
    '   key  - Valid key object.
    '   data - Dictionary of key value pairs for the data to create the Datastream with 
    '
    ' Returns: New Datastream object or dictionary containing any exceptions and errors that occured
    '''

    ds = DataStream(owner=key.owner)
    for attr, val in data['ds_data'].iteritems():

        if attr == "scaling_function":
            try:
                sc = ScalingFunction.objects.get(name=val)
            except ScalingFunction.DoesNotExist as e:
                error = "From createDs: scaling function with name '%s' does not exist." % str(val)
                return {"error": error, "exception": str(e)}

            setattr(ds, attr, sc)
        else:
            try:
                setattr(ds, attr, val)
            except Exception as e:
                error = "From createDs: There was a problem setting '%s' with the value '%s'." % (str(attr), str(val))
                return {"error": error, "exception": str(e)}
    try:
        ds.full_clean()
        ds.save()
    except ValidationError as e:
        error = "From createDs: There were one or more problems setting DataStream attributes."
        return {"error": error, "exception": str(e)}

    return ds


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
