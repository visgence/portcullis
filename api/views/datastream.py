"""
" api/views/datastream.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"    Jerry Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#System Imports
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View

try:
    import simplejson as json
except ImportError:
    import json

from django.db import transaction
import time

#Local Imports
from graphs.models import DataStream, ScalingFunction, Sensor
from api.utilities import cors_http_response_json
from portcullis.models import PortcullisUser as User
from check_access import check_access


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


def updateObject(obj, data):
    for field, fieldData in data.iteritems():
        #No manual setting of ids
        if field in ['id', 'pk']:
            continue

        setattr(obj, field, fieldData)

    try:
        obj.full_clean()
        obj.save()
    except ValidationError as e:
        return [{field: error} for field, error in e.message_dict.iteritems()]
    except Exception as e:
        return ["There was an unexpected error while saving a %s: %s" % (obj.__class__.__name__, str(e))]

    return obj


def create(sensor, owner, data):
    '''
    ' Create or updates a DataStream. If an existing DataStream can be found by a sensor or owner/name combo then
    ' that sensor will be updated.  Otherwise a new DataStream will be created.
    '
    ' Keyword Args: 
    '   sensor - Sensor instance that is used to help determine if we need to update a DataStream or create one. If a new 
    '            DataStream gets created then the new DataStream will claim the sensor. 
    '   owner  - User object that either owns an existing DataStream to update or will own the new DataStream that get's 
    '            created.
    '   data   - Dict of data to update/create a DataStream with.
    '
    ' Returns: DataStream instance if a DataStream was updated/created successfully else an error
    '''

    if not isinstance(sensor, Sensor):
        return "Was not given a sensor while trying to create/update a DataStream"

    name = data.get('name', '')
    ds = DataStream.objects.claimedBySensor(sensor)
    if ds is None:
        try:
            ds = DataStream.objects.get(owner=owner, name=name)
        except DataStream.DoesNotExist:
            ds = None

    if isinstance(owner, User) and ds is not None and ds.owner != owner:
        return "Invalid Credentials"

    ds = DataStream() if ds is None else ds

    if 'scaling_function' in data:
        sfName = data['scaling_function']
        try:
            sf = ScalingFunction.objects.get(name=sfName)
        except ScalingFunction.DoesNotExist:
            return "There is no Scaling Function with the name \'%s\'"%str(sfName) 
    else:
        sf = ScalingFunction.objects.get(name="Identity")

    extra = {'sensor': sensor, 'scaling_function': sf}
    if owner is not None:
        extra.update({'owner': owner})

    data.update(extra)
    updatedDs = updateObject(ds, data)
    return updatedDs 


class DataStreamView(View):

    def get(self, request):
        
        returnData = {
            'errors': []
            ,'streams': []
        }

        user = check_access(request)
        if not isinstance(user, User):
            returnData['errors'].append('User authentication failed.')
            return HttpResponse(json.dumps(returnData), content_type="application/json", status_code=401)
   
        streams = DataStream.objects.get_viewable(user)
        returnData['streams'] = [s.toDict() for s in streams]

        return HttpResponse(json.dumps(returnData, indent=4), content_type="application/json")

