"""
" portcullis/ajax.py
" Contributing Authors:
"    Evan Salazar   (Visgence, Inc)
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2013 Visgence, Inc.
"""

# System imports
try: import simplejson as json
except ImportError: import json
from dajaxice.decorators import dajaxice_register
from django.core import serializers
from django.db import models
from django.contrib.auth.models import User

# Local imports
from portcullis.models import DataStream
from portcullis.views.crud import genModel

# TODO:  All this needs access checkers!!
@dajaxice_register
def read_source(request, model_name):
    '''
    ' Returns all data from a given model as serialized json.
    ' 
    ' Keyword Args: 
    '    model_name - The model name to get serialized data from
    '''

    cls = models.loading.get_model('portcullis', model_name)

    return serialize_model_objs(cls.objects.all())  

@dajaxice_register
def update_model_obj(request, data, model_name):
    '''
    ' Updates a given models object with new data. 
    ' 
    ' Keyword Args: 
    '    data       - The new data to update the object with.
    '    model_name - The model name that the updating object belongs to. 
    '''

    cls = models.loading.get_model('portcullis', model_name)

    try:
         obj = cls.objects.get(id=data['id'])
    except Exception as e:
        return json.dumps({'errors': 'Can not load object: Exception: ' + str(e)})

    return alter_model_obj(obj, data) 

@dajaxice_register
def create_model_obj(request, data, model_name):
    '''
    ' Creates a given model object with using the data given.
    ' 
    ' Keyword Args: 
    '    data       - The data to create the object with.
    '    model_name - The model name that the new object belongs to. 
    '''
    
    cls = models.loading.get_model('portcullis', model_name)
    obj = cls() 
    return alter_model_obj(obj, data) 
    

def alter_model_obj(obj, data):
    '''
    ' Modifies a model object with the given data, saves it to the db and 
    ' returns it as serialized json.
    '
    ' Keyword Args:
    '    obj  - The model object to modify.
    '    data - The data to modify the object with.
    '
    ' Returns:
    '    The modified object serialized as json. 
    '''
    
    fields = genModel(obj.__class__)['fields'].items()
    m2m = []
    try:
        for field, properties in fields:
            print 'Adding properties to obj ' + field
            if properties['editable']:
                if properties['django_m2m']:
                    m2m.append((field, properties))
                    continue
                
                if properties['django_related_field']:
                    cls = models.loading.get_model(
                        properties['django_related_app'], properties['django_related_cls'])
                    rel_obj = cls.objects.get(id=data[field])
                    setattr(obj, field, rel_obj)
                else:
                    setattr(obj, field, data[field])

        obj.save()
    except Exception as e:
        print 'In create_datastream exception: ' + str(e)
        return json.dumps({'errors': 'Can not save datastream: Exception: ' + str(e)})
    return serializers.serialize('json', [obj])

@dajaxice_register
def destroy(request, data):
    try:
        ds = DataStream.objects.get(id = data['id'])
    except Exception as e:
        return json.dumps({'errors': 'Could not delete: Exception: ' + str(e)})

    ds.delete()
    return serializers.serialize("json", DataStream.objects.all())

def serialize_model_objs(objs):
    '''
    ' Takes a list of model objects and returns the serialization of them.
    '
    ' Keyword Args:
    '    objs - The objects to serialize
    '''
    new_objs = []
    for obj in objs:
        fields = obj._meta.fields
        obj_dict = {}
        for f in fields:
            obj_dict[f.attname] = f.value_to_string(obj)

        new_objs.append(obj_dict)
        
    return json.dumps(new_objs, indent=4)



