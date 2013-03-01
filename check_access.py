'''
' checkAccess.py
' Contributing Authors:
'    Jeremiah Davis (visgence, Inc)
'
' (c) 2013 Visgence, Inc.
'''

# System imports
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
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
    if not request.user.is_active:
        return HttpResponse(json.dumps({'errors': 'Error: User is not active.'}), mimetype='application/json')

    if isinstance(request.user, AnonymousUser):
        return PortcullisUser(is_active=True)

    try:
        return request.user.portcullisuser
    except Exception as e:
        

# TODO: Make useful for a single page app.
    if(request.user.username == ''):
        return HttpResponseRedirect("/portcullis/greeting/?next=%s" % urlquote(request.get_full_path()))

    t = loader.get_template('login.html');

    if(not request.user.is_active):
        c = Context({'user':request.user,'access_error':'User is not active'});
        return HttpResponse(t.render(c))

    return 0;
