"""
" portcullis/views/shared_view.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


# System Imports
from django.contrib.auth 
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
try: import simplejson as json
except ImportError: import json

# Local Imports
from portcullis.models import SharedView, Key


def sharedView(request, token):
    '''
    ' This view will render the main page for sharing views, with the divs
    ' for widgets.  The widgets will be loaded with ajax after page load.
    '''
    # validate the token, consuming a use if applicable
    key = Key.objects.validate(token)
    if not isinstance(key, Key):
        raise Http404(key)

    # Load the instance, if there is one.
    view = SavedView.objects.get(key = key)

    t = loader.get_template('sharedView.html')
    c = RequestContext(request, {'view':view,
                                 'start':view.widget.all()[0].saveddsgraph.start,
                                 'end':view.widget.all()[0].saveddsgraph.end,
                                 'granularity':view.widget.all()[0].saveddsgraph.end,
                                 })

    return HttpResponse(t.render(c))
    
