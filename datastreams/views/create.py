"""
" datastreams/views/create.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#System Imports
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
try: import simplejson as json
except ImportError: import json

#Local Imports
from portcullis.models import DataStream, Key, ScalingFunction

@require_POST
@csrf_exempt
def createDs(request):
    '''
    ' Creates a DataStream with data from json and with the owner of the specified token.  
    '
    ' Returns: HttpResponse with Json containing the new DataStreams id or error is anything went wrong.
    '''

    #TODO: for now screw permissions, but later, put them in!!
    
    return_data = {}
    try: 
        json_data = json.loads(request.POST.get("jsonData"))
    except Exception as e:
        return_data['error'] = "From createDs: Problem getting json data from request."
        return_data['exception'] = str(e)
        return HttpResponse(json.dumps(return_data), mimetype="application/json")

    try:
        key = Key.objects.get(key = json_data['token'])
    except Key.DoesNotExist as e:
        return_data['error'] = "From createDs: Key with token '%s' does not exist."%str(json_data['token'])
        return_data['exception'] = str(e)
        return HttpResponse(json.dumps(return_data), mimetype="application/json")

    ds = DataStream()
    for attr, val in json_data['ds_data'].iteritems():
        if attr == "scaling_function":
            try:
                sc = ScalingFunction.objects.get(name=val)
            except ScalingFunction.DoesNotExist as e:
                return_data['error'] = "From createDs: scaling function with name '%s' does not exist."%str(val)
                return_data['exception'] = str(e)
                return HttpResponse(json.dumps(return_data), mimetype="application/json")
            setattr(ds, attr, sc)
        else:
            try:
                setattr(ds, attr, val) 
            except Exception as e:
                return_data['error'] = "From createDs: There was a problem setting '%s' with the value '%s'."%(str(attr), str(val))
                return_data['exception'] = str(e)
                return HttpResponse(json.dumps(return_data), mimetype="application/json")

    ds.owner = key.owner  
  
    try:
        #Make sure this ds doesn't already exist
        existant_ds = DataStream.objects.get(owner = ds.owner, name = ds.name)  
        return_data['id'] = existant_ds.pk
    except DataStream.DoesNotExist as e:
        try:
            ds.full_clean()
            ds.save()
            return_data['id'] = ds.pk
        except ValidationError as e:
            return_data['error'] = "From createDs: There were one or more problems setting DataStream attributes."
            return_data['exception'] = str(e)
 
    return HttpResponse(json.dumps(return_data), mimetype="application/json")

