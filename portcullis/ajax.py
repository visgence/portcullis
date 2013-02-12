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

# Local imports
from portcullis.models import DataStream

# TODO:  All this needs access checkers!!
@dajaxice_register
def read_datastream(request):
    return serializers.serialize("json", DataStream.objects.all())

@dajaxice_register
def create_datastream(request, data):
    print data['description']
    return serializers.serialize('json', [DataStream.objects.get(id = 15)])

