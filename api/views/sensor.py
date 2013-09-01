

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
from graphs.models import Sensor, ClaimedSensor, DataStream
from portcullis.models import PortcullisUser as User
from api.utilities import cors_http_response_json
from api.views.datastream import claimDs


def createObject(cls, data):
    obj = cls()
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


def claimSensor(sensor, name, owner):
    try:
        claimedSensor = ClaimedSensor.objects.get(name=name, owner=owner)
    except ClaimedSensor.DoesNotExist:
        data = {'name': name, 'owner': owner, 'sensor': sensor}
        claimedSensor = createObject(ClaimedSensor, data)

    return claimedSensor


@transaction.commit_manually
def create(data, owner):
    try:
        try:
            uuid = data['uuid']
        except KeyError:
            transaction.rollback()
            return "A sensor uuid is required"

        try:
            name = data['name']
        except KeyError:
            transaction.rollback()
            return str(uuid)+": A sensor name is required"

        #Get sensor or create one
        try:
            sensor = Sensor.objects.get(uuid=uuid)
        except Sensor.DoesNotExist:
            sensor = createObject(Sensor, data)
            if not isinstance(sensor, Sensor):
                transaction.rollback()
                return sensor

        #Get/create a claimed sensor and if we dont get one back error
        claimedSensor = claimSensor(sensor, name, owner)
        if not isinstance(claimedSensor, ClaimedSensor):
            transaction.rollback()
            return claimedSensor

        dsName = owner.email
        if owner.first_name != '':
            dsName = owner.first_name
        dsName += "|"+claimedSensor.name
        data['name'] = dsName 

        ds = claimDs(claimedSensor, data)
        if not isinstance(ds, DataStream):
            transaction.rollback()
            return ds

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
    ' Creates a list of sensors to a owner given the proper credentials for that owner and the data
    ' to create the sensor if it does not exist.
    ' 
    ' Owner must provide their email and password for authentication.
    ' 
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

    try:
        email = jsonData['email']
        user = User.objects.get(email=email)
    except KeyError:
        returnData['errors'].append('Email required')
        return cors_http_response_json(returnData, 404)
    except User.DoesNotExist:
        returnData['errors'].append('User with email %s does not exist' % str(email))
        return cors_http_response_json(returnData, 404)

    for s in sensors:
        sensor = create(s, user)
        #Assume error string if not a sensor
        if not isinstance(sensor, Sensor):
            returnData['errors'].append(sensor)
        else:
            returnData['sensors'].append(sensor.toDict())

    return cors_http_response_json(returnData)



