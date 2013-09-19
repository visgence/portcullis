"""
" api/views/reading_loader.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#Django Imports
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist

#System Imports
try:
    import simplejson as json
except ImportError:
    import json
import time
import urllib

#Local Imports
from graphs.models import DataStream, SensorReading, Sensor
from portcullis.customExceptions import SensorReadingCollision
from api.utilities import cors_http_response, cors_http_response_json


@csrf_exempt
@require_POST
def add_reading(request):
    '''
    ' Adds a single reading to the database. To insert a reading we need a uuid from a sensor and its value
    ' that it wants to post.
    '''
    timestamp = int(time.time())

    try:
        uuid = request.POST['uuid']
    except KeyError:
        return cors_http_response("A uuid is required", 404)

    try:
        value = request.POST['value']
        if(value is None or value == ""):
            return cors_http_response("No data was passed for insertion!", 404)
    except KeyError:
        return cors_http_response("A value is required", 404)

    try:
        sensor = Sensor.objects.get(uuid=uuid)
        claimedSensor = ClaimedSensor.objects.get(sensor=sensor)
        datastream = DataStream.objects.get(claimed_sensor=claimedSensor)
    except Sensor.DoesNotExist:
        return cors_http_response("There is no sensor for the uuid \'%s\'" % str(uuid), 404)
    except ClaimedSensor.DoesNotExist:
        return cors_http_response("Sensor with uuid \'%s\' is not claimed!"%str(uuid), 404)
    except DataStream.DoesNotExist:
        return cors_http_response("There is no datastream for the sensor with uuid %s"%str(uuid), 404)
     
    #Insert
    try:
        insert_reading(datastream, sensor, value, timestamp)
    except SensorReadingCollision as e:
        return cors_http_response(e, 500)
    except ValidationError as e:
        msg = "There was one or more errors while saving a sensor reading: "
        msg += ", ".join([field+": "+error for field, error in e.message_dict.iteritems()])
        return cors_http_response(msg, 500)

    return cors_http_response('Successfully inserted record')


def add_readings(readings, streamId=None):
    '''
    ' Adds multiple readings to the database from a list of lists in the form of 
    ' [[sensor_uuid, value1, time1], [sensor_uuid, value2, time2]...] with time being optional.
    '
    ' Keyword Args:
    '   readings - List of lists containing sensor uuid, sensor reading, and timestamp values.
    '   stream   - Optional. Id of Datastream to specifically look for to post sensor value to.
    '              If stream is found sensor uuid's must match sensor claimed by stream.
    '
    ' Returns: HttpResponse with json encoded Dict object with the following data:
    '    {
    '       "insertions_attempted": <number of readings attemtped to be inserted>
    '       "insertions_succeeded": <number of successfull readings inserted>
    '       "insertions_failed": <number of failed reading insertions>
    '       "errors": <List of errors strings. If applicable>
    '    }
    '''

    returnData = {
        'insertions_attempted': 0
        ,'insertions_succeeded': 0
        ,'insertions_failed': 0
        ,'errors': []
    }

    if not isinstance(readings, list):
        returnData['errors'].append("Did not recieve a list of sensor readings")
        return cors_http_response_json(returnData)
   
    ds = None
    if streamId is not None:
        try:
            ds = DataStream.objects.get(id=streamId)
        except DataStream.DoesNotExist:
            returnData['errors'].append("Datastream with id '%s' does not exist."%str(streamId))
            return cors_http_response_json(returnData)
  
    #Grab all reading from the json
    for reading in readings:
        uuid = None
        raw_sensor_value = None
        timestamp = None
       
        returnData['insertions_attempted'] += 1
        
        try:
            uuid = reading[0]
            raw_sensor_value = reading[1]
            timestamp = reading[2]
        except:
            pass

        #If no sensor value then skip this reading
        if(raw_sensor_value is None or raw_sensor_value == ""):
            returnData['errors'].append("Missing data to insert! Please be sure to give data to insert.")
            continue

        #If a stream was provided make sure it's sensor matches the current uuid
        if ds is not None and (ds.sensor is None or ds.sensor.uuid != uuid):
            error = "Sensor with uuid '%s' is not claimed by Datastream with id '%s'"%(str(uuid), str(streamId))
            returnData['errors'].append(error)
            continue

        #Attempt to get a stream if one wasn't provided
        if ds is None:
            try:
                ds = DataStream.objects.get(sensor__uuid=uuid)
            except DataStream.DoesNotExist:
                returnData['errors'].append("No Datastream that has claimed Sensor with uuid '%s'"%str(uuid))
                return cors_http_response_json(returnData, 400)
                continue
                
        try:
            insert_reading(ds, ds.sensor, raw_sensor_value, timestamp)
            returnData['insertions_succeeded'] += 1
        except SensorReadingCollision as e:
            returnData['errors'].append(str(e))


    returnData['insertions_failed'] = returnData['insertions_attempted'] - returnData['insertions_succeeded']
    return cors_http_response_json(returnData)


def insert_reading(ds, sensor, value, timestamp=None):
    ''' 
    ' Insert a sensor reading into the database.
    ' If there is already an entry for the given timestamp and datastream, it will throw
    ' an exception.
    '
    ' Keyword Args:
    '   ds        - The DataStream instance this reading cooresponds to.
    '   sensor    - The Sensor instanct this reading cooresponds to.
    '   value     - The data value for this sensor reading.
    '   timestamp - Optional. The time of the sensor reading. If no time is
    '               given, this method will stamp it with the current time.
    '
    ' Returns: Newly inserted reading instance.
    '''

    if timestamp is None:
        timestamp = int(time.time())

    # Make sure that we are not causing a collision in the table.
    try:
        sr = SensorReading.objects.get(timestamp=timestamp, datastream=ds)
        raise SensorReadingCollision('Sensor Reading with id \'%s\' already exists.' % str(sr.id))
    except ObjectDoesNotExist:
        pass

    reading = SensorReading(datastream=ds, sensor=sensor, value=value, timestamp=timestamp)
    reading.full_clean()
    reading.save()
    return reading


class SensorReadingView(View):

    def post(self, request, streamId=None):
        
        try:
            readings = json.loads(request.body)
        except (TypeError, ValueError):
            return cors_http_response("Bad Json", 400)

        if streamId is not None:
            return add_readings(readings, streamId)
        else:
            return add_readings(readings)

