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
from django.db import IntegrityError
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
#@transaction.commit_manually
def create_datastreams(request):
    '''
    ' Creates DataStreams with an array of data from json and with the owner of the specified token.
    '
    ' The json required format is the following: TBD
    '
    ' Returns: HttpResponse with Json containing a list with the new DataStream's ids and a dictionary of errors
    '''
    timingMark = time.time()
    #TODO: for now screw permissions, but later, put them in!!
    
    errors = []

    try:
        json_data = json.loads(request.POST.get("jsonData"))
    except Exception as e:
        #transaction.rollback()
        errors.append({ 'error': "Missing jsonData from request.", 'exception': str(e) })
        return cors_http_response_json(errors)
    
    if 'key' in json_data:
        try:
            key = Key.objects.get(key=json_data['key'])
        except Key.DoesNotExist as e:
            #transaction.rollback()
            errors.append({'error': 'Key not in Database: ' + str(json_data['key']), 'exception': str(e)})
            return cors_http_response_json(errors)
    else:
        #transaction.rollback()
        errors.append({'error': 'No Key received.', 'exception': None})
        return cors_http_response_json(errors)

    owner = key.owner

    if 'datastreams' not in json_data:
        #transaction.rollback()
        errors.append({ 'error': 'No datastream data received', 'exception': None })
        return cors_http_response_json(errors)

    if not isinstance(json_data['datastreams'], list):
        #transaction.rollback()
        errors.append({'error': 'Datastream object not a list.', 'exception': None})
        return cors_http_response_json(errors)

    return_ids = {}
    for data in json_data['datastreams']:
             
        try:
            ds_name = data['name']
        except Exception as e:
            error = "Exception getting DataStream name %s." % type(e) 
            errors.append({"error": error, "exception": str(e)})
            continue
        
        try:
            ds = create_ds(owner, data) 

            #If not a ds then an error
            if not isinstance(ds, DataStream):
                errors.append(ds)
                continue

        except (IntegrityError, ValidationError) as e:
            try:
                ds = DataStream.objects.get(name=ds_name, owner=owner)
            except DataStream.DoesNotExist:
                error = 'Unexpected error getting datastream!  Datastream does not exist, but could not create.'
                errors.append({'error': error, 'exception': str(e)})
                continue

        return_ids[ds_name] = ds.pk
        ds.can_read.add(key)
        ds.can_post.add(key)

    #transaction.commit()
    elapsedTime = time.time() - timingMark
    return cors_http_response_json({'ids': return_ids, "errors": errors, "time": elapsedTime})


def create_ds(owner, data):
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
    timingMark = time.time()
    ds = DataStream(owner=owner)
    for attr, val in data.iteritems():

        if attr == "scaling_function":
            try:
                sc = ScalingFunction.objects.get(name__iexact=val)
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
    print 'Assign attr time: %f' % (time.time() - timingMark)
    timingMark = time.time()
    try:
        ds.full_clean()
        ds.save()
    except ValidationError as e:
        unique_error = u'Data stream with this Owner and Name already exists.'
        if '__all__' in e.message_dict and unique_error in e.message_dict['__all__']:
            raise e
        error = "There were one or more problems setting DataStream attributes."
        return {"error": error, "exception": str(e)}
    print 'Clean and save time: %f' % (time.time() - timingMark)
    print
    return ds


