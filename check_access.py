'''
' checkAccess.py
' Contributing Authors:
'    Jeremiah Davis (visgence, Inc)
'
' (c) 2013 Visgence, Inc.
'''

# System imports
from django.http import HttpResponse
try: import simplejson as json
except ImportError: import json

# Local imports
from portcullis.models import PortcullisUser

def check_access(request):
    '''
    ' If the request user resolves to a portcullisUser, return that.
    ' If the request user is an AnonymousUser, return an 'Anonymous' PortcullisUser
    '  (just a PortcullisUser Object with nothing set).
    ' If the request user is not active, return an error.
    '''

    if request.user.is_authenticated():
        if request.user.is_active:
            try:
                return request.user.portcullisuser
            except Exception as e:
                return HttpResponse(json.dumps(
                        {'errors': 'Error: User %s is not a PortcullisUser.' % request.user.username}
                        ), mimetype='application/json')
        else:
            return HttpResponse(json.dumps({'errors': 'Error: User %s is not active.' % request.user.username}),
                                mimetype='application/json')
    # Anonymous user
    else:
        return None
