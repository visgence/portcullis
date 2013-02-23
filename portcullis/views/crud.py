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
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
try: import simplejson as json
except ImportError: import json

# Local Imports
from portcullis.models import DataStream, PortcullisUser


def model_grid(request, model_name):
    '''
    ' View to return the html that will hold a models crud. 
    '''

    t = loader.get_template('crud.html')
    c = RequestContext(request, {'model_name': model_name})
    return HttpResponse(t.render(c), mimetype="text/html")

def genColumns(modelObj):
    
    columns = []
    for f in get_meta_fields(modelObj):
       
        #We don't care about these fields
        if f.name.endswith('_ptr'):
            continue

        field = {'field':f.name,'name':f.name.title(), 'id': f.name} 
        #if f.name in ['name', 'id']:
        #    field['sortable'] = True
        # Make sure to give the type and other meta data for the columns.
        if f.primary_key or not f.editable:
            field['_editable'] = False
        else:
            field['_editable'] = True
    
        # Figure out the type of field.
        d_type = f.db_type(connections.all()[0])
        if isinstance(f, models.ForeignKey):
            field['model_name'] = f.rel.to.__name__
            field['_type'] = 'foreignkey'
        elif d_type == 'boolean':
            field['_type'] = 'boolean'
        elif d_type in ['integer', 'serial']:
            field['_type'] = 'integer'
        elif d_type.startswith('numeric'):
            field['_type'] = 'number'
        elif d_type.startswith('timestamp'):
            field['_type'] = 'date'
        elif d_type == 'text':
            field['_type'] = 'text'
        elif d_type.find('char') > -1:
            field['_type'] = 'char'
        else:
            field['_type'] = d_type # Any other type will default to a text widget.
            

        columns.append(field)
    for m in get_meta_m2m(modelObj):
        columns.append({
            'field':m.name, 
            'name':m.name.title(), 
            'id':m.name,
            'model_name': m.rel.to.__name__,
            '_type': 'm2m',
            '_editable': True
        })

    return columns

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
