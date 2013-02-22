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
from portcullis.views.crud import genModel, genColumns

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
         obj = cls.objects.get(pk=data['pk'])
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
    
@dajaxice_register
def update(request, model_name, data):
    '''
    ' Modifies a model object with the given data, saves it to the db and 
    ' returns it as serialized json.
    '
    ' Keyword Args:
    '    model_name  - The name of the model object to modify.
    '    data - The data to modify the object with.
    '
    ' Returns:
    '    The modified object serialized as json. 
    '''

    cls = models.loading.get_model('portcullis', model_name)

    if 'pk' not in data:
        obj = cls()
    else:
        try:
            obj = cls.objects.get(pk = data['pk'])
        except Exception as e:
            return json.dumps({'errors': 'Cannot load object to save: Exception: ' + e.message})

    fields = genModel(obj.__class__)['fields'].items()
    m2m = []
    try:
        for field, properties in fields:
            if properties['editable'] and data[field] not in [None, '']:
                if properties['django_m2m']:
                    m2m.append((field, properties))
                    continue
                    
                elif properties['django_related_field']:
                    cls = models.loading.get_model(
                        properties['django_related_app'], properties['django_related_cls'])
                    rel_obj = cls.objects.get(pk=data[field]['pk'])
                    setattr(obj, field, rel_obj)
                else:
                    setattr(obj, field, data[field])

        obj.save()
    except Exception as e:
        print 'In create_datastream exception: ' + str(e)
        return json.dumps({'errors': 'Can not save object: Exception: ' + str(e)})
    
    return serialize_model_objs([obj.__class__.objects.get(pk = obj.pk)]) 

@dajaxice_register
def destroy(request, model_name, data):
    '''
    ' Receive a model_name and data object via ajax, and remove that item,
    ' returning either a success or error message.
    '''
    cls = models.loading.get_model('portcullis', model_name)
    try:
        ds = cls.objects.get(pk = data['pk'])
    except Exception as e:
        return json.dumps({'errors': 'Could not delete: Exception: %s: %s' % (str(type(e)), e.message)})

    ds.delete()
    return json.dumps({'success': 'Successfully deleted item with primary key: %s' % data['pk']})

@dajaxice_register
def get_columns(request, model_name):
    '''
    ' Return a JSON serialized column list for rendering a grid representing a model.
    '
    ' Keyword args:
    '   model_name - The name of the model to represent.
    '''
    cls = models.loading.get_model('portcullis', model_name)
    return json.dumps(genColumns(cls))

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
        m2m_fields = obj._meta.many_to_many
        obj_dict = {}
        
        for f in fields:
            if isinstance(f, models.fields.related.ForeignKey) or \
                    isinstance(f, models.fields.related.OneToOneField):
                obj_dict[f.name] = {
                    '__unicode__': getattr(obj, f.name).__unicode__(),
                    'pk': f.value_from_object(obj),
                    'model_name': f.rel.to.__name__
                }
            else:
                if '__unicode__' not in obj_dict:
                    obj_dict['__unicode__'] = obj.__unicode__()

                obj_dict[f.name] = f.value_from_object(obj)
                if type(obj_dict[f.name]) not in [dict, list, unicode, int, long, float, bool, type(None)]:
                    obj_dict[f.name] = f.value_to_string(obj)

        for m in m2m_fields:
            m_objs = getattr(obj, m.name).all()
            obj_dict[m.name] = []
            for m_obj in m_objs:
                obj_dict[m.name].append({
                    '__unicode__': m_obj.__unicode__(),
                    'pk': m_obj.pk,
                    'model_name': m.rel.to.__name__
                })

        if 'pk' not in obj_dict:
            obj_dict['pk'] = obj.pk

        new_objs.append(obj_dict)
    print new_objs
    return json.dumps(new_objs, indent=4)



