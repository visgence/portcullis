#System Imports
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import time
import urllib

#Local Imports
from portcullis.models import DataStream, SensorReading, Key
from portcullis.customExceptions import SensorReadingCollision

@csrf_exempt
def add_reading(request):
    '''
    Adds a single reading to the database. In order to insert a reading we either need a stream id. 
    '''

    datastream_id = request.REQUEST.get('datastream_id')
    node_id = request.REQUEST.get('node_id')
    port_id = request.REQUEST.get('port_id')
    auth_token = request.REQUEST.get('auth_token')
    raw_sensor_value = request.REQUEST.get('value')

    if(Key.objects.validate(auth_token) == None):
        return HttpResponse('Incorrect Authentication!')

    #Is there even any data?
    if(raw_sensor_value is None or raw_sensor_value == ""):
        return HttpResponse("No data was passed for insertion! Please be sure to pass some data. Example: value=233")
    # Get the data stream to insert to.
    try:
        # First try to use the datastream_id
        datastream = DataStream.objects.get(id = datastream_id)
    except ObjectDoesNotExist:
        try:
            # If that fails, try the node/port combination.  This is for backwards compatability,
            # but since these fields are not unique together, it is dangerous.
            datastream = DataStream.objects.get(node_id = node_id, port_id = port_id)
        except ObjectDoesNotExist:
            return HttpResponse('Invalid Datastream')
        except MultipleObjectsReturned:
            return HttpResponse('Multiple Objects Returned.  Node/Port are no longer unique together.  Please ' +
                                'use a DataStream id.')
    #Insert
    insert_reading(datastream, raw_sensor_value)
    return HttpResponse('Successfully inserted record')

def add_reading_bulk_hash(request):
    '''
    Adds multiple readings at "once". If for any reading there is a port, node, and sensor value then we insert the reading otherwise we record 
    an error and continue with the other readings. 

    Works just like add_reading_bulk except incoming data is in a list of hashes instead of a list of lists.
    '''

    auth_token = request.GET.get('auth_token')
    json_text = urllib.unquote(request.GET.get('json'))

    if(Key.objects.validate(auth_token) == None):
        return HttpResponse('Incorrect Authentication!')

    if(json_text is None): 
        return HttpResponse("No json received. Please send a serialized array of hashes in the form [{port=port1, node=node1, value=value1, stream=stream1, time=time1}, ...]")

    readings = simplejson.loads(json_text)
    insertion_attempts = 0
    insertion_successes = 0
    error_string = ''

    for reading in readings:
        time = None
        node_id = None
        port_id = None
        data_stream = None
        raw_sensor_value = None

        insertion_attempts += 1
        
        try:
            node_id = reading['node']
            port_id = reading['port']
        except:
            pass

        try:
            raw_sensor_value = reading['value']
        except:
            pass

        try:
            time = reading['time']
        except:
            pass

        try:
            data_stream['stream']
        except:
            pass
        
        #If no sensor value then skip reading
        if(raw_sensor_value is None):
            error_string += "\nNo data was passed for insertion! The information that was sent was: \ntime=%(time)s\nnode_id=%(node)s\nport_id=%(port)s\ndata_stream=%(stream)s\n" % {'time':time, 'node':node_id, 'port':port_id, 'stream':data_stream}

        else:
            #If no port or node skip reading
            if(node_id is not None and port_id is not None):
                stream_info = validate_stream(None, node_id, port_id)
                if(stream_info['error']):
                    error_string += stream_info['error'] 
                else:
                    insert_reading(stream_info['datastream'], raw_sensor_value)
                    insertion_successes += 1
            else:
                error_string += "\nNot enough info to uniquely identify a data stream. The information that was sent was: \ntime=%(time)s\nnode_id=%(node)s\nport_id=%(port)s\ndata_stream=%(stream)s\nvalue=%(raw_sensor_value)s" % {'time':time, 'node':node_id, 'port':port_id, 'stream':data_stream, 'raw_sensor_value':raw_sensor_value};

    #Give a message based on number of insertions, attempts, errors etc
    if(error_string is '' and insertion_attempts != 0):
        success_message = "\n\nTotal Insertion Attempts: %s" % insertion_attempts
        success_message += "\n\nSuccessful Insertions : %s" % insertion_successes
        success_message += "\n\nAll records inserted!"
        return HttpResponse(success_message)
    else:
        error_string += "\n\nTotal Insertion Attempts: %s" % insertion_attempts
        error_string += "\n\nSuccessful Insertions : %s" % insertion_successes
        failed_insertions = insertion_attempts - insertion_successes
        error_string += "\n\nFailed Insertions : %s" % failed_insertions
        return HttpResponse(error_string)

@csrf_exempt
def add_reading_bulk(request):
    '''
    Adds multiple readings at "once". If for any reading there is a port, node, and sensor value then we insert the reading otherwise we record 
    an error and continue with the other readings.
    '''

    auth_token = request.REQUEST.get('auth_token')
    try:
        json_text = urllib.unquote(request.REQUEST.get('json'))
    except:
        return HttpResponse("No json received. Please send a serialized array of arrays in the form [[node_id1,port_id1,value1],[node_id2,port_id2,value2]]")

    if(Key.objects.validate(auth_token) == None):
        return HttpResponse('Incorrect Authentication!')

    readings = simplejson.loads(json_text)
    insertion_attempts = 0
    insertion_successes = 0
    error_string = ''
    
    #Grab all reading from the json
    for reading in readings:
        node_id = None
        port_id = None
        raw_sensor_value = None

        insertion_attempts += 1
        
        try:
            node_id = reading[0]
            port_id = reading[1]
            raw_sensor_value = reading[2]
        except:
            pass

        #If no sensor value then skip this reading
        if(raw_sensor_value is None or raw_sensor_value == ""):
           error_string += "\nNo data was passed for insertion! Please be sure to pass some data.\n"
        else:
            #if no port or node then skip this reading
            if((node_id is not None and node_id != "") and (port_id is not None and port_id != "")):
                stream_info = validate_stream(None, node_id, port_id)
                if(stream_info['error']):
                    error_string += stream_info['error'] 
                else:
                    insert_reading(stream_info['datastream'], raw_sensor_value)
                    insertion_successes += 1
            else:
                error_string += "\nNot enough info to uniquely identify a data stream.You must give both a node_id and a port_id.\n "

    #Give a message based on number of insertions, attempts, errors etc
    if(error_string is '' and insertion_attempts != 0):
        success_message = "\n\nTotal Insertion Attempts: %s" % insertion_attempts
        success_message += "\n\nSuccessful Insertions : %s" % insertion_successes
        success_message += "\n\nAll records inserted!"
        return HttpResponse(success_message)
    else:
        error_string += "\n\nTotal Insertion Attempts: %s" % insertion_attempts
        error_string += "\n\nSuccessful Insertions : %s" % insertion_successes
        failed_insertions = insertion_attempts - insertion_successes
        error_string += "\n\nFailed Insertions : %s" % failed_insertions
        return HttpResponse(error_string)
    

@csrf_exempt
def add_list(request):
    '''
    Adds multiple readings to the database from a list of lists.  Might it be better to use a list of 
    dictionaries?  This has been renamed from add_bulk_readings so that the old add_bulk_readings can be
    add back for backwards compatability.
    '''

    auth_token = request.REQUEST.get('auth_token')
    try:
        json_text = urllib.unquote(request.REQUEST.get('json'))
    except:
        return HttpResponse("No json received. Please send a serialized array of arrays in the form [[datastream_id,value1,time1],[datastream_id,value2,time2]].  time is optional.")

    if(Key.objects.validate(auth_token) == None):
        return HttpResponse('Incorrect Authentication!')

    readings = simplejson.loads(json_text)
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

        # Get the datastream, if possible
        try:
            ds = DataStream.objects.get(id = ds_id)
            insert_reading(ds, raw_sensor_value, timestamp)
            insertion_successes += 1
        except ObjectDoesNotExist:
            error_string += "\nInvalid DataStream.\n"
        except SensorReadingCollision as e:
            error_string += '\n' + str(e) + '\n'

    #Give a message based on number of insertions, attempts, errors etc
    if(error_string is '' and insertion_attempts != 0):
        success_message = "\n\nTotal Insertion Attempts: %s" % insertion_attempts
        success_message += "\n\nSuccessful Insertions : %s" % insertion_successes
        success_message += "\n\nAll records inserted!"
        return HttpResponse(success_message)
    else:
        error_string += "\n\nTotal Insertion Attempts: %s" % insertion_attempts
        error_string += "\n\nSuccessful Insertions : %s" % insertion_successes
        failed_insertions = insertion_attempts - insertion_successes
        error_string += "\n\nFailed Insertions : %s" % failed_insertions
        return HttpResponse(error_string)




def insert_reading(datastream, raw_sensor_value, timestamp = None):
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
        sr = SensorReading.objects.get(timestamp = timestamp, datastream = datastream)
        raise SensorReadingCollision('Sensor Reading with id \'%s\' already exists.' % str(sr.id))
    except ObjectDoesNotExist:
        pass
    
    reading = SensorReading(datastream = datastream, value = raw_sensor_value, timestamp = timestamp )
    reading.save()
    



def validate_stream(stream_id, node_id, port_id):
    '''
        Checks to make sure a given stream exists or not. It either checks by using the streams id or by checking the node/port id pairing.

        Paramters:
            stream_id = The id of the DataStream to check
            node_id   = A node id that can be checked with a port id
            port_id   = A port id that can be checked with a node id

        Returns:
            A dictionary with the datastream id upon succesfull verification and an error message otherwise.
            Keys:
                datastream_id = Datastream id or null
                error         = Error message or null
    '''
    
    if(stream_id != None and stream_id != ''):
        stream = None
        try:
            stream = DataStream.objects.get(id = stream_id)
        except:
            pass

        if(stream):
            return {'datastream':stream, 'error':''}
        else:
            return {'error':"\ndatastream_id %s does not exist in the datastream table.\n" % stream_id}

    elif((node_id != None and node_id != '') and (port_id != None and port_id != '')):
        stream = None
        try:
            stream = DataStream.objects.get(node_id = node_id, port_id = port_id)
        except:
            pass

        if(stream):
            return {'datastream':stream, 'error':''}
        else:
            return {'error':"\nNode id %s and port id %s does not map to an existing datastream id.\n" % (node_id, port_id)}

    return {'error':"Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.\"\n\n" }
