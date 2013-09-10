"""
" portcullis/views/signup.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#Local Imports
from portcullis.models import PortcullisUser
from api.views.login import login

#Django Imports
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.template import loader, RequestContext

#System Imports
try:
    import simplejson as json
except ImportError:
    import json


def signupPage(request):

    t = loader.get_template('signup_page.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


def signup(request):

    try:
        data = json.loads(request.POST['signupData'])
    except KeyError:
        return HttpResponseNotFound('No form data.')
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Bad json.')

    email = data.get('email', '')
    firstName = data.get('first-name', '')
    lastName = data.get('last-name', '')
    password = data.get('password', '')
    passwordRepeat = data.get('password-repeat', '')
    
    if email == '':
        error = {'error': "An email address is required", 'field': 'email'}
        return HttpResponse(json.dumps(error), content_type="application/json")
    try:
        PortcullisUser.objects.get(email=email)
        error = {'error': "A user already exists with that email", 'field': 'email'}
        return HttpResponse(json.dumps(error), content_type="application/json")
    except PortcullisUser.DoesNotExist:
        pass

    if firstName == '':
        error = {'error': "Please give your first name", 'field': 'first-name'}
        return HttpResponse(json.dumps(error), content_type="application/json")
    
    if lastName == '':
        error = {'error': "Please give your last name", 'field': 'last-name'}
        return HttpResponse(json.dumps(error), content_type="application/json")
   
    if password == '':
        error = {'error': "A password is required", 'field': 'password'}
        return HttpResponse(json.dumps(error), content_type="application/json")

    if passwordRepeat == '' or password != passwordRepeat:
        error = {'error': "Passwords do not match", 'field': 'password-repeat'}
        return HttpResponse(json.dumps(error), content_type="application/json")

    PortcullisUser.objects.create_user(email, firstName, lastName, password)
    login(request, email, password) 

    return HttpResponse(json.dumps('success'), content_type="application/json")
