'''
' portcullis/views/login.py
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

                data = {
                    'greeting': greeting_page.render(greeting_c),
                }

                resp = HttpResponse(json.dumps(data), mimetype="application/json")
                resp['Access-Control-Allow-Origin'] = '*'
                return resp
            else:
                error = "This account is disabled"
        else:
            error = "Invalid username and/or password"

    return_data = {'error': error}
    resp = HttpResponse(json.dumps(return_data), mimetype="application/json")
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('portcullis-index'))


def password_form(request):
    '''
    ' This view will render the change password request form.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        resp = HttpResponse(json.dumps({'errors': portcullisUser.content}), mimetype='application/json')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    if not isinstance(portcullisUser, AuthUser):
        error = 'User must be logged in to change password.'
        resp = HttpResponse(json.dumps({'errors': error}), mimetype='application/json')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp

    t = loader.get_template('passwordForm.html')
    c = RequestContext(request, {'user': portcullisUser})
    
    resp = HttpResponse(json.dumps({'html': t.render(c)}), mimetype='application/json')
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


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
        return portcullisUser
    if not isinstance(portcullisUser, AuthUser):
        errors = 'Please log in before changing your password.'
        resp = HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp

    jsonData = request.REQUEST.get('jsonData', None)

    try:
        jsonData = json.loads(jsonData)
    except Exception as e:
        errors = 'JSON Exception: %s: %s' % (type(e), e.message)
        resp = HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp

    try:
        oldPassword = jsonData['oldPassword']
        newPassword = jsonData['newPassword']
    except KeyError as e:
        errors = 'KeyError: %s' % e.message
        resp = HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp

    # Make sure old password is valid
    user = authenticate(username=portcullisUser.get_username(), password=oldPassword)
    if user is None or user != portcullisUser:
        errors = 'Authentication Error: Username and password are not correct'
        resp = HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    elif not user.is_active:
        errors = 'Authentication Error: User is not active.  You must be active to change password.'
        resp = HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')
        resp['Access-Control-Allow-Origin'] = '*'
        return resp

    # Change the password
    portcullisUser.set_password(newPassword)
    portcullisUser.save()
    success = 'Password successfully changed!'
    resp = HttpResponse(json.dumps({'success': success}), mimetype='application/json')
    resp['Access-Control-Allow-Origin'] = '*'
    return resp
