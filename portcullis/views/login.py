#Local Imports
from portcullis.views.user_portal import user_streams

#System Imports
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout as auth_logout
try: import simplejson as json
except ImportError: import json


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
    greeting_c.update(csrf(request));
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

                streams_page = user_streams(request) 
                data = {
                    'streams_html': streams_page, 
                    'greeting':greeting_page.render(greeting_c),
                }
            
                return HttpResponse(json.dumps(data), mimetype="application/json")
            else:
                error = "This account is disabled"
        else:
            error = "Invalid username and/or password";

    return_data = {'error':error}
    return HttpResponse(json.dumps(return_data), mimetype="application/json")

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('portcullis-index'))

