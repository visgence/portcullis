"""
" portcullis/views/shared_view.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


# System Imports
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
try: import simplejson as json
except ImportError: import json
from datetime import datetime

# Local Imports
from portcullis.models import SavedView, Key
from graphs.data_reduction import reductFunc


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


    dateformat = '%Y/%m/%d %H:%M:%S'
    start = datetime.utcfromtimestamp(view.widget.all()[0].saveddsgraph.start)
    end = datetime.utcfromtimestamp(view.widget.all()[0].saveddsgraph.end)
    t = loader.get_template('sharedView.html')
    c = RequestContext(request, {'view': view,
                                 'start': start,
                                 'end': end,
                                 'granularity': view.widget.all()[0].saveddsgraph.granularity,
                                 'reductions': reductFunc.keys(),
                                 'token': token
                                 })

    return HttpResponse(t.render(c))
    
