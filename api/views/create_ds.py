"""
" api/views/create_ds.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"    Jerry Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#System Imports
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
try:
    import simplejson as json
except ImportError:
    import json

from django.db import transaction
import time

#Local Imports
from portcullis.models import DataStream, Key, ScalingFunction
from api.utilites import cors_http_response_json


@require_POST
@csrf_exempt
@transaction.commit_manually
def create_datastreams(request):
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
    ' Returns: HttpResponse with Json containing a list with the new DataStream's ids and a dictionary of errors
    '''
    timingMark = time.time()
    #TODO: for now screw permissions, but later, put them in!!
    
    errors = []

    try:
        json_data = json.loads(request.POST.get("jsonData"))
    except Exception as e:
        transaction.rollback()
        errors.append({ 'error': "Missing jsonData from request.", 'exception': str(e) })
        return cors_http_response_json(errors)
    
    #jsonData should contain a list of data.
    if not isinstance(json_data, list):
        transaction.rollback()
        errors.append({ 'error': "jsonData is not a list.", 'exception': None })
        return cors_http_response_json(errors)

    return_ids = {}
    for data in json_data:
        
        try:
            key = Key.objects.get(key=data['token'])
        except Key.DoesNotExist as e:
            error = "Key with token '%s' does not exist." % str(data['token'])
            errors.append({"error": error, "exception": str(e)})
            continue
        except KeyError as e:
            errors.append({"error": "The key 'token' does not exist in the dictionary jsonData.", "exception": str(e)})
            continue
        
        try:
            ds_name = data['ds_data']['name']
        except Exception as e:
            error = "Exception getting DataStream name %s." % type(e) 
            errors.append({"error": error, "exception": str(e)})
            continue
        
        try:
            ds = DataStream.objects.get(name=ds_name, owner=key.owner)
        except DataStream.DoesNotExist:
            ds = create_ds(key, data) 

            #If not a ds then an error
            if not isinstance(ds, DataStream):
                errors.append(ds)
                continue

        return_ids[ds_name] = ds.pk
        ds.can_read.add(key)
        ds.can_post.add(key)

    transaction.commit()
    elapsedTime = time.time() - timingMark
    return cors_http_response_json({'ids': return_ids, "errors": errors, "time": elapsedTime})


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
                error = "ScalingFunction with the name '%s' does not exist." % str(val)
                return {"error": error, "exception": str(e)}

            setattr(ds, attr, sc)
        else:
            try:
                setattr(ds, attr, val)
            except Exception as e:
                error = "There was a problem setting '%s' with the value '%s'." % (str(attr), str(val))
                return {"error": error, "exception": str(e)}
    try:
        ds.full_clean()
        ds.save()
    except ValidationError as e:
        error = "There were one or more problems setting DataStream attributes."
        return {"error": error, "exception": str(e)}

    return ds


