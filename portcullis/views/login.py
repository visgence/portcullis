#Local Imports
from portcullis.views.user_portal import user_streams

#System Imports
from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
import urlparse
import json


def render_main_page(request):

    greeting_temp = loader.get_template('login.html');
    greeting_c = RequestContext(request, {'user': request.user})
    greeting_c.update(csrf(request));

    main_page = loader.get_template('main_page.html')
    main_c = RequestContext(request, {'greeting': greeting_temp.render(greeting_c) })
    return HttpResponse(main_page.render(main_c))

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
    return HttpResponseRedirect("/portcullis/greeting/")

