"""
" api/utilites.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

# System Imports
from django.http import HttpResponse
try:
    import simplejson as json
except ImportError:
    import json


def cors_http_response_json(content, status=200):
    '''
    ' Creates and returns a HttpRespone object that allows cross site access through Cors 
    ' with json serialized content.
    '
    ' Keyword Arguements:
    '   content - Object that is json serialized into the content of the HttpResponse object.
    '   status  - Optional status code to give the response object. Default is 200
    '
    ' Return: HttpResponse that allows cross site access with serialized json content.
    '''

    resp = HttpResponse(json.dumps(content), content_type="application/json", status=status)
    resp['Access-Control-Allow-Origin'] = '*'
    return resp

def cors_http_response(content, status=200):
    '''
    ' Creates and returns a HttpRespone object that allows cross site access through Cors.
    '
    ' Keyword Arguements:
    '   content - String that will become the content of the HttpResponse
    '   status  - Optional status code to give the response object. Default is 200
    '
    ' Return: HttpResponse that allows cross site access with string content
    '''

    resp = HttpResponse(content, content_type="text/html", status=status)
    resp['Access-Control-Allow-Origin'] = '*'
    return resp
