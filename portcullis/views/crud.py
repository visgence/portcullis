"""
" portcullis/views/crud.py
" Contributing Authors:
"    Evan Salazar   (Visgence, Inc)
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2013 Visgence, Inc.
"""

# System Imports
from django.core import serializers
from django.http import HttpResponse
from django.template import RequestContext, loader
try: import simplejson as json
except ImportError: import json

# Local Imports
from portcullis.models import DataStream

def crudjs(request):
    '''
    ' View to return dynamic javascript for the DataStream crud interface.  May be extended
    ' to do other models also.
    '''
    t = loader.get_template('crud.js')
    c = RequestContext(request, {
            'model': json.dumps(genModel(DataStream), indent=4),
            'columns': json.dumps(genColumns(DataStream), indent=4)
            })
    return HttpResponse(t.render(c), mimetype="text/javascript")

def datastream(request):
    t = loader.get_template('ds_crud.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), mimetype="text/html")


def read(request):

    jsonData  = serializers.serialize("json", DataStream.objects.all())
    return HttpResponse(jsonData, mimetype="application/json")

def genModel(modelObj):
   
    model = {};
    model['id'] = modelObj._meta.pk.name
    
    fields = {}

    for f in modelObj._meta.fields:
        if f.unique:
            fields[f.name] = {'editable':False}
        else:
            fields[f.name] = {'editable':True}


    model['fields'] = fields
    return model

def genColumns(modelObj):
    
    columns = []
    for f in modelObj._meta.fields:
        columns.append({'field':f.name,'title':f.name})
    return columns

def model(request):
    jsonData = {'model':genModel(datastream.models.DataStream)}
    return HttpResponse(json.dumps(jsonData,indent=4), mimetype="application/json")
