'''
' checkAccess.py
' Contributing Authors:
'    Jeremiah Davis (visgence, Inc)
'
' (c) 2013 Visgence, Inc.
'''

# System imports
from django.http import HttpResponse
from django.contrib.auth import get_user_model
AuthUser = get_user_model()
try:
    import simplejson as json
except ImportError:
    import json


def check_access(request):
    '''
    ' If the request user resolves to a portcullisUser, return that.
    ' If the request user is an AnonymousUser, return None
    ' If the request user is not active, return an error.
    '''

    if request.user.is_authenticated():
        if request.user.is_active:
            return request.user
        else:
            return HttpResponse(json.dumps({'errors': 'Error: User %s is not active.' % request.user.username}),
                                mimetype='application/json')
    return None
