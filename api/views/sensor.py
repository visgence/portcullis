"""
" api/views/stream.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#Django Imports
from django.db import transaction
from django.core.exceptions import ValidationError
from django.views.generic import View
from django.http import HttpResponse

#System Imports
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from graphs.models import Sensor, DataStream
from portcullis.models import PortcullisUser as User
from api.utilities import cors_http_response_json
from api.views.datastream import create as createDs
from check_access import check_access


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


@transaction.commit_manually
def claimSensor(data, owner):
    try:
        
        try:
            uuid = data['uuid']
            sensor = Sensor.objects.get(uuid=uuid)
        except KeyError:
            transaction.rollback()
            return "A sensor uuid is required"
        except Sensor.DoesNotExist:
            sensor = None
      
        #Cases for if a user has no authority to create/claim sensors
        if (sensor is None and owner is None) or \
           (sensor is not None and not sensor.isClaimed() and owner is None):

            transaction.rollback()
            return "Invalid Credentials"
      
        sensor = Sensor() if sensor is None else sensor
        
        #If sensor isnt claimed and we have credentials
        if not sensor.isClaimed() and owner is not None:
            sensor = updateObject(sensor, data)
            if not isinstance(sensor, Sensor):
                transaction.rollback()
                return sensor

        streamData = data.get('stream_data', {})

        ds = createDs(sensor, owner, streamData)
        if not isinstance(ds, DataStream):
            transaction.rollback()
            return ds

        #We've successfully set up everything for the sensor so return it
        transaction.commit()
        return sensor 
    except Exception as e:
        transaction.rollback()
        return str(e)


class SensorView(View):

    def post(self, request):
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
            sensor = claimSensor(s, user)
            
            #Assume error string if not a sensor
            if not isinstance(sensor, Sensor):
                if isinstance(sensor, list):
                    returnData['errors'].extend(sensor)
                else:
                    returnData['errors'].append(sensor)
            else:
                returnData['sensors'].append(sensor.toDict())

        return cors_http_response_json(returnData)


    def get(self, request):
        returnData = {
            'errors': []
            ,'sensors': []
        }

        user = check_access(request)
        if not isinstance(user, User):
            returnData['errors'].append('User authentication failed.')
            return HttpResponse(json.dumps(returnData), content_type="application/json", status_code=401)
       
        sensors = Sensor.objects.filter(datastream__owner=user)
        returnData['sensors'] = [s.toDict() for s in sensors]
        
        return HttpResponse(json.dumps(returnData), content_type="application/json")
       

