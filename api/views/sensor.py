

#Django Imports
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError

#System Imports
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from graphs.models import Sensor, ClaimedSensor, DataStream, ScalingFunction
from portcullis.models import PortcullisUser as User
from api.utilities import cors_http_response_json
from api.views.datastream import claimDs


def updateObject(obj, data):
    for field, fieldData in data.iteritems():
        #No manual setting of ids
        if field in ['id', 'pk']:
            continue

        try:
            setattr(obj, field, fieldData)
        except ValueError as e:
            return "There was a problem assigning a value to a %s: %s" % (obj.__class__.__name__, str(e))

    try:
        obj.full_clean()
        obj.save()
    except ValidationError as e:
        return [{field: error} for field, error in e.message_dict.iteritems()]
    except Exception as e:
        return "There was an unexpected error while saving a %s: %s" % (obj.__class__.__name__, str(e))

    return obj


def claimSensor(sensor, name, owner):
    
    #First try to update sensor by owner/name combo.  This allows us to update the which sensor is claimed.
    #If that doesn't work try to locate the claimed sensor by it's sensor which will allow the sensors 
    #name and/or owner to be updated. Otherwise just create one.
    data = {'name': name, 'owner': owner, 'sensor': sensor}
    try:
        claimedSensor = updateObject(ClaimedSensor.objects.get(name=name, owner=owner), data)
    except ClaimedSensor.DoesNotExist:
        try:
            claimedSensor = updateObject(ClaimedSensor.objects.get(sensor=sensor), data)
        except ClaimedSensor.DoesNotExist:
            claimedSensor = updateObject(ClaimedSensor(), data)

    return claimedSensor


@transaction.commit_manually
def create(data, owner):
    try:
        
        try:
            uuid = data['uuid']
            sensor = Sensor.objects.get(uuid=uuid)
        except KeyError:
            transaction.rollback()
            return "A sensor uuid is required"
        except Sensor.DoesNotExist:
            sensor = None
      
        #See if the sensor is claimed or not
        claimedSensor = ClaimedSensor.objects.claimed(sensor)

        #Cases for if a user has no authority to create/claim sensors
        if (sensor is None and owner is None) or \
           (sensor is not None and claimedSensor is None and owner is None):

            transaction.rollback()
            return "Invalid Credentials"
      
        name = data.get('name', '')
        sensor = Sensor() if sensor is None else sensor
        
        #If sensor isnt claimed and we have credentials
        if claimedSensor is None and owner is not None:
            sensor = updateObject(sensor, data)
            if not isinstance(sensor, Sensor):
                transaction.rollback()
                return sensor

            claimedSensor = claimSensor(sensor, name, owner)
            if not isinstance(claimedSensor, ClaimedSensor):
                transaction.rollback()
                return claimedSensor

        #We've successfully set up everything for the sensor so return it
        transaction.commit()
        return sensor 
    except Exception as e:
        transaction.rollback()
        return str(e)


@csrf_exempt
@require_POST
def createSensors(request):
    '''
    ' Accepts a list of sensors and their data as json and will make sure they are claimed.
    ' User credentials are necessary to claiming unclaimed sensors unless the sensor is already claimed
    ' in which case the sensor will simply update itself.
    ' 
    ' Owner must provide their email and password for authentication to create and claim sensor.  
    '''

    returnData = {
        'errors': []
        ,'sensors': []
    }

    try:
        jsonData = json.loads(request.body)
    except KeyError:
        returnData['errors'].append('No json sent')
        return cors_http_response_json(returnData, 404)
    except (TypeError, ValueError):
        returnData['errors'].append('Bad Json')
        return cors_http_response_json(returnData, 404)

    sensors = jsonData.get('sensors', [])
    if len(sensors) == 0:
        returnData['errors'].append('There was no sensor data sent')
        return cors_http_response_json(returnData, 404)


    user = None
    try:
        email = jsonData['email']
        user = User.objects.get(email=email)
    except KeyError:
        pass
    except User.DoesNotExist:
        returnData['errors'].append('User with email %s does not exist' % str(email))
        return cors_http_response_json(returnData, 404)

    for s in sensors:
        sensor = create(s, user)
        
        #Assume error string if not a sensor
        if not isinstance(sensor, Sensor):
            if isinstance(sensor, list):
                returnData['errors'].extend(sensor)
            else:
                returnData['errors'].append(sensor)
        else:
            returnData['sensors'].append(sensor.toDict())
            
            ds_data = s.get('ds_data', None)
            if ds_data is not None:
                claimedSensor = ClaimedSensor.objects.claimed(sensor)
                ds = claimDs(claimedSensor, ds_data)
                if not isinstance(ds, DataStream):
                    returnData['errors'] = ds

    return cors_http_response_json(returnData)



