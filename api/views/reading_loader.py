"""
" api/views/reading_loader.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


#System Imports
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
try:
    import simplejson as json
except ImportError:
    import json
import time
import urllib

#Local Imports
from graphs.models import DataStream, SensorReading
from portcullis.customExceptions import SensorReadingCollision
from api.utilites import cors_http_response


@csrf_exempt
def add_reading(request):
    '''
    Adds a single reading to the database. In order to insert a reading we either need a stream id.
    '''

    datastream_id = request.REQUEST.get('datastream_id')
    auth_token = request.REQUEST.get('auth_token')
    raw_sensor_value = request.REQUEST.get('value')

    key = Key.objects.validate(auth_token)
    if key is None:
        return cors_http_response('Incorrect Authentication!')

    #Is there even any data?
    if(raw_sensor_value is None or raw_sensor_value == ""):
        return cors_http_response("No data was passed for insertion! Please be sure to pass some data. Example: value=233")

    if datastream_id is None or datastream_id == '':
        return cors_http_response('Cannot identify datastream, please give datastream_id.')

    # get and validate datastream permission
    try:
        datastream = DataStream.objects.get_ds_and_validate(datastream_id, key, 'post')
    except DataStream.DoesNotExist as e:
        datastream = 'Error: %s' % (e,)
    except ValueError as e:
        datastream = 'Error: Internal validation error.'
    # Assume if we don't get a DS object we get an error string.
    if not isinstance(datastream, DataStream):
        return cors_http_response(datastream)

    #Insert
    try:
        insert_reading(datastream, raw_sensor_value)

    except SensorReadingCollision as e:
        return cors_http_response(e)
    
    return cors_http_response('Successfully inserted record')


@csrf_exempt
def add_list(request, auth_token=None):
    '''
    Adds multiple readings to the database from a list of lists.  Might it be better to use a list of
    dictionaries?  This has been renamed from add_bulk_readings so that the old add_bulk_readings can be
    add back for backwards compatability.
    '''
    try:
        if auth_token is None:
            auth_token = request.REQUEST.get('auth_token')

        try:
            json_text = urllib.unquote(request.REQUEST.get('json'))
        except:
            try:
                json_text = urllib.unquote(request.REQUEST.get('d'))
            except:
                msg = "No json received. Please send a serialized array of arrays in the form [[datastream_id,value1,time1],[datastream_id,value2,time2]].  time is optional."
                return cors_http_response(msg)

        key = Key.objects.validate(auth_token)
        if key is None:
            return cors_http_response('Incorrect Authentication!')

        try:
            readings = json.loads(json_text)
        except Exception as e:
            return cors_http_response('Error: Invalid JSON: %s: %s' % (type(e), e.message))

        insertion_attempts = 0
        insertion_successes = 0
        error_string = ''

        #Grab all reading from the json
        for reading in readings:
            ds_id = None
            raw_sensor_value = None
            timestamp = None

            insertion_attempts += 1

            try:
                ds_id = reading[0]
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
                ds = DataStream.objects.get_ds_and_validate(ds_id, key, 'post')
            except DataStream.DoesNotExist as e:
                ds = str(e)
            except ValueError as e:
                ds = str(e)
            if not isinstance(ds, DataStream):
                error_string += '\n' + ds + '\n'
            else:
                try:
                    insert_reading(ds, raw_sensor_value, timestamp)
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


def insert_reading(datastream, raw_sensor_value, timestamp=None):
    ''' Insert a sensor reading into the database.
    ' This method will insert the given values into the given datastream.
    ' If there is already an entry for the given timestamp, it will throw
    ' an exception.
    '
    ' Keyword Args:
    '   datastream - The DataStream object this reading cooresponds to, or the id.
    '   raw_sensor_value - The data value for this sensor reading.
    '   timestamp - The time of the sensor reading.  Deault None.  If no time is
    '               given, this method will stamp it with the current time.
    '''

    if timestamp is None:
        timestamp = int(time.time())

    # Make sure that we are not causing a collision in the table.
    try:
        sr = SensorReading.objects.get(timestamp=timestamp, datastream=datastream)
        raise SensorReadingCollision('Sensor Reading with id \'%s\' already exists.' % str(sr.id))
    except ObjectDoesNotExist:
        pass

    reading = SensorReading(datastream=datastream, value=raw_sensor_value, timestamp=timestamp)
    reading.save()
