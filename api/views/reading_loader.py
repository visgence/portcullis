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
from django.core.exceptions import ObjectDoesNotExist

#System Imports
try:
    import simplejson as json
except ImportError:
    import json
import time
import urllib

#Local Imports
from graphs.models import DataStream, SensorReading, Sensor, ClaimedSensor
from portcullis.customExceptions import SensorReadingCollision
from api.utilities import cors_http_response


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


@csrf_exempt
def add_reading_list(request):
    '''
    Adds multiple readings to the database from a list of lists.  Might it be better to use a list of
    dictionaries?  This has been renamed from add_bulk_readings so that the old add_bulk_readings can be
    add back for backwards compatability.
    '''

    try:
        try:
            print request.body
            readings = json.loads(request.body)
        except KeyError:
            msg = "No json received. Please send a serialized array of arrays in the form "
            msg += "[[sensor_uuid,value1,time1],[sensor_uuid,value2,time2]].  time is optional."
            return cors_http_response(msg)
        except (TypeError, ValueError):
            return cors_http_response("Bad Json", 404)

        insertion_attempts = 0
        insertion_successes = 0
        error_string = ''

        #Grab all reading from the json
        for reading in readings:
            uuid = None
            raw_sensor_value = None
            timestamp = None

            insertion_attempts += 1

            try:
                uuid = reading[0]
                raw_sensor_value = reading[1]
                timestamp = reading[2]
            except:
                pass

            #If no sensor value then skip this reading
            if(raw_sensor_value is None or raw_sensor_value == ""):
                error_string += "\nNo data was passed for insertion! Please be sure to pass some data.\n"
                continue

            # Get the datastream, if possible
            try:
                ds = DataStream.objects.get(claimed_sensor__sensor__uuid=uuid)
            except DataStream.DoesNotExist as e:
                ds = str(e)
            except ValueError as e:
                ds = str(e)
            if not isinstance(ds, DataStream):
                error_string += '\n' + ds + '\n'
            else:
                try:
                    insert_reading(ds, ds.claimed_sensor.sensor, raw_sensor_value, timestamp)
                    insertion_successes += 1
                except SensorReadingCollision as e:
                    error_string += '\n' + str(e) + '\n'

        #Give a message based on number of insertions, attempts, errors etc
        if(error_string is '' and insertion_attempts != 0):
            success_message = "\n\nTotal Insertion Attempts: %s" % insertion_attempts
            success_message += "\n\nSuccessful Insertions : %s" % insertion_successes
            success_message += "\n\nAll records inserted!"
            return cors_http_response(success_message)
        else:
            error_string += "\n\nTotal Insertion Attempts: %s" % insertion_attempts
            error_string += "\n\nSuccessful Insertions : %s" % insertion_successes
            failed_insertions = insertion_attempts - insertion_successes
            error_string += "\n\nFailed Insertions : %s" % failed_insertions
            return cors_http_response(error_string)

    except Exception as e:
        return cors_http_response('Unexpected error occured! Exception: %s: %s' % (type(e), e.message))


def insert_reading(ds, sensor, value, timestamp=None):
    ''' 
    ' Insert a sensor reading into the database.
    ' If there is already an entry for the given timestamp and datastream, it will throw
    ' an exception.
    '
    ' Keyword Args:
    '   ds        - The DataStream instance this reading cooresponds to, or the id.
    '   sensor    - The Sensor instanct this reading cooresponds to, or the id.
    '   value     - The data value for this sensor reading.
    '   timestamp - The time of the sensor reading.  Deault None.  If no time is
    '               given, this method will stamp it with the current time.
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

