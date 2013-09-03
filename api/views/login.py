'''
' api/views/login.py
'
' Contributing Authors:
'    Jeremiah Davis (Visgence, Inc.)
'    Bretton Murphy (Visgence, Inc.)
'
' (c) 2013 Visgence, Inc.
'''


#System Imports
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
AuthUser = get_user_model()
try:
    import simplejson as json
except ImportError:
    import json

# Local Imports
from check_access import check_access
from api.utilities import cors_http_response_json


def user_login(request):

    error = ''

    if request.method == 'POST':
        json_data = json.loads(request.POST['json_data'])

        user = authenticate(username=json_data["username"], password=json_data["password"])
        if user is not None:
            if user.is_active:
                login(request, user)

                greeting_page = loader.get_template('greeting.html')
                greeting_c = RequestContext(request, {})
    
                nav_t = loader.get_template('nav_bar.html')
                nav_c = RequestContext(request, {})

                data = {
                    'greeting': greeting_page.render(greeting_c),
                    'nav': nav_t.render(nav_c)
                }

                return cors_http_response_json(data)
            else:
                error = "This account is disabled"
        else:
            error = "Invalid username and/or password"

    return cors_http_response_json({'error': error})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('portcullis-index'))


def password_form(request):
    '''
    ' This view will render the change password request form.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        return cors_http_response_json({'errors': portcullisUser.content})
    if not isinstance(portcullisUser, AuthUser):
        return cors_http_response_json({'errors': 'User must be logged in to change password.'})

    t = loader.get_template('passwordForm.html')
    c = RequestContext(request, {'user': portcullisUser})
    return cors_http_response_json({'html': t.render(c)})


@require_POST
def change_password(request):
    '''
    ' This view will allow a user to change their password.
    '
    ' POST arguments:
    '   jsonData - JSON data containing:
    '              oldPassword - string containing user's current password.
    '              newPassword - string containing password to change to.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        return cors_http_response_json({'errors': portcullisUser.content})
    if not isinstance(portcullisUser, AuthUser):
        return cors_http_response_json({'errors': 'Please log in before changing your password.'})

    jsonData = request.REQUEST.get('jsonData', None)

    try:
        jsonData = json.loads(jsonData)
    except Exception as e:
        return cors_http_response_json({'errors': 'JSON Exception: %s: %s' % (type(e), e.message)})

    try:
        oldPassword = jsonData['oldPassword']
        newPassword = jsonData['newPassword']
    except KeyError as e:
        return cors_http_response_json({'errors': 'KeyError: %s' % e.message})

    # Make sure old password is valid
    user = authenticate(username=portcullisUser.get_username(), password=oldPassword)
    if user is None or user != portcullisUser:
        return cors_http_response_json({'errors': 'Authentication Error: Username and password are not correct'})
    elif not user.is_active:
        error = 'Authentication Error: User is not active.  You must be active to change password.'
        return cors_http_response_json({'errors': error})

    # Change the password
    portcullisUser.set_password(newPassword)
    portcullisUser.save()
    return cors_http_response_json({'success': 'Password successfully changed!'})
