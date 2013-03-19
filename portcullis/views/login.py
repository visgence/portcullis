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
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.views.decorators.http import require_POST
try:
    import simplejson as json
except ImportError:
    import json

# Local Imports
from check_access import check_access
from portcullis.models import PortcullisUser


def greeting(request):
    '''
    ' Render the greeting or login html in the main page.
    '''

    # TODO: When check_access is updated, may use it here.

    if request.user.is_authenticated() and request.user.is_active:
        greeting_temp = loader.get_template('greeting.html')
    else:
        greeting_temp = loader.get_template('login.html')

    greeting_c = RequestContext(request, {'user': request.user})
    greeting_c.update(csrf(request))
    return greeting_temp.render(greeting_c)


def user_login(request):

    error = ''

    #Read next url to be redirected to
    try:
        redirect_to = request.REQUEST["next"]
    except KeyError:
        pass

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

                return HttpResponse(json.dumps(data), mimetype="application/json")
            else:
                error = "This account is disabled"
        else:
            error = "Invalid username and/or password"

    return_data = {'error': error}
    return HttpResponse(json.dumps(return_data), mimetype="application/json")


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('portcullis-index'))


def passwordForm(request):
    '''
    ' This view will render the change password request form.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        return HttpResponse(json.dumps({'errors': portcullisUser.content}), mimetype='application/json')
    if not isinstance(portcullisUser, PortcullisUser):
        error = 'User must be logged in to change password.'
        return HttpResponse(json.dumps({'errors': error}), mimetype='application/json')

    t = loader.get_template('passwordForm.html')
    c = RequestContext(request, {'user': portcullisUser})

    return HttpResponse(json.dumps({'html': t.render(c)}), mimetype='application/json')


@require_POST
def changePassword(request):
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
    if not isinstance(portcullisUser, PortcullisUser):
        errors = 'Please log in before changing your password.'
        return HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')

    jsonData = request.REQUEST.get('jsonData', None)

    try:
        jsonData = json.loads(jsonData)
    except Exception as e:
        errors = 'JSON Exception: %s: %s' % (type(e), e.message)
        return HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')

    try:
        oldPassword = jsonData['oldPassword']
        newPassword = jsonData['newPassword']
    except KeyError as e:
        errors = 'KeyError: %s' % e.message
        return HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')

    # Make sure old password is valid
    user = authenticate(username=portcullisUser.username, password=oldPassword)
    if user is None or user != portcullisUser.user_ptr:
        errors = 'Authentication Error: Username and password are not correct'
        return HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')
    elif not user.is_active:
        errors = 'Authentication Error: User is not active.  You must be active to change password.'
        return HttpResponse(json.dumps({'errors': errors}), mimetype='application/json')

    # Change the password
    portcullisUser.set_password(newPassword)
    portcullisUser.save()
    success = 'Password successfully changed!'
    return HttpResponse(json.dumps({'success': success}), mimetype='application/json')
