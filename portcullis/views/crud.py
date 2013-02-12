"""
" portcullis/views/crud.py
" Contributing Authors:
"    Evan Salazar   (Visgence, Inc)
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2013 Visgence, Inc.
"""

# System Imports
from django.db import models, connections
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

def create(request):
    print request.GET.items()
    return HttpResponse(json.dumps(request.GET), mimetype='application/json')
    #print json.loads(request.POST['jsonData'])
    #return HttpResponse(request.GET['jsonData'], mimetype="application/json")

def genModel(modelObj):
   
    model = {};
    model['id'] = modelObj._meta.pk.name
    
    fields = {}

    for f in get_meta_fields(modelObj):
        fields[f.name] = {}
        if f.unique or not f.editable:
            fields[f.name]['editable'] = False

        # Figure out the type of field.
        d_type = f.db_type(connections.all()[0])
        if d_type == 'boolean':
            fields[f.name]['type'] = 'boolean'
            #fields[f.name]['validation'] = {'required': True}
        elif d_type in ['integer', 'serial'] or d_type.startswith('numeric'):
            fields[f.name]['type'] = 'number'
        elif d_type.startswith('timestamp'):
            fields[f.name]['type'] = 'date'
        # Default is string
            
    for m in get_meta_m2m(modelObj):
        fields[m.name] = {'editable': False}
        
    model['fields'] = fields
    return model

def genColumns(modelObj):
    
    columns = []
    for f in get_meta_fields(modelObj):
        field = {'field':f.name,'title':f.name.title()}
        if f.name in ['name', 'id']:
            field['sortable'] = True
        columns.append(field)
    for m in get_meta_m2m(modelObj):
        columns.append({'field':m.name, 'title':m.name.title()})
    return columns

def model(request):
    jsonData = {'model':genModel(datastream.models.DataStream)}
    return HttpResponse(json.dumps(jsonData,indent=4), mimetype="application/json")

def get_meta_fields(cls):
    '''
    ' Use a model class to get the _meta fields.
    '''
    return cls._meta.fields

def get_meta_m2m(cls):
    '''
    ' Use a model class to get the _meta ManyToMany fields
    '''
    return cls._meta.many_to_many
