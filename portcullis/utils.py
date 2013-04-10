'''
' portcullis/utils.py
' Contributing Authors:
'    Jeremiah Davis (Visgence, Inc)
'
' (c) 2013 Visgence, Inc.
'''
try:
    import simplejson as json
except ImportError:
    import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    '''
    ' Extend the json encoder to encode decimal numbers as floats.
    '''

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)
