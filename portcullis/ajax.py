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


# Local imports
from portcullis.models import DataStream
from portcullis.views.crud import genModel

# TODO:  All this needs access checkers!!
@dajaxice_register
def read_datastream(request):
    return serializers.serialize("json", DataStream.objects.all())

@dajaxice_register
def create_datastream(request, data):
    fields = genModel(DataStream)['fields'].items()
    ds = DataStream()
    m2m = []
    try:
        for field, properties in fields:
            print 'Adding properties to ds ' + field
            if properties['editable']:
                if properties['django_m2m']:
                    m2m.append((field, properties))
                    continue
                
                if properties['django_related_field']:
                    cls = models.loading.get_model(
                        properties['django_related_app'], properties['django_related_cls'])
                    rel_obj = cls.objects.get(id=data[field])
                    setattr(ds, field, rel_obj)
                else:
                    setattr(ds, field, data[field])

        ds.save()
    except Exception as e:
        print 'In create_datastream exception: ' + str(e)
        return json.dumps({'errors': str(e)})
    return serializers.serialize('json', [ds])

