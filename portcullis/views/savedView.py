"""
" portcullis/views/savedView.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


# System Imports
from django.core.urlresolvers import reverse
from django.db.transaction import commit_on_success
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.template import RequestContext, loader
from django.views.decorators.http import require_POST
from django.utils import timezone
try: import simplejson as json
except ImportError: import json
from datetime import datetime, timedelta

# Local Imports
from portcullis.models import SavedView, Key, DataStream
from graphs.models import SavedDSGraph
from graphs.data_reduction import reductFunc
from graphs.views.display_graphs import graphs_list

def savedView(request, token):
    '''
    ' This view will render the main page for sharing views, with the divs
    ' for widgets.  The widgets will be loaded with ajax after page load.
    '
    ' TODO: When other kinds of  widgets are added, add them to the page also.
    '''
    # validate the token, consuming a use if applicable
    key = Key.objects.validate(token)
    if not isinstance(key, Key):
        raise Http404(key)

    # Load the instance, if there is one.
    view = SavedView.objects.get(key = key)
    streams = [ w.saveddsgraph.datastream for w in view.widget.all()]

    t = loader.get_template('graph_container.html')
    c = RequestContext(request, {'graphs': graphs_list(streams),
                                 'token': token
                                 })

    return HttpResponse(t.render(c))

@commit_on_success
@require_POST
def createSavedView(request):
    '''
    ' Create a savedView and return the token or link for that shared view.
    '''

    try:
        portcullisUser = request.user.portcullisuser
    except ObjectDoesNotExist:
        # TODO: Should not be a return, should be a raise, but don't have a 403 right now,
        #But should be okay, because save has not been called yet.
        return HttpResponseForbidden('Must be logged in to create saved view')

    if 'jsonData' not in request.POST:
        raise Http404('Unrecognized data')

    jsonData = json.loads(request.POST['jsonData'])

    expires = timezone.now() + timedelta(days=7)
    key = Key.objects.generateKey(portcullisUser, 'Saved view', expires, 20)

    # Create a SavedView object and graphs, and save data.
    savedView = SavedView.objects.create(key = key)

    start = jsonData['start']
    end = jsonData['end']
    gran = jsonData['granularity']
    # Not doing in a try catch, because should be gotten from existing graphs
    for graphData in jsonData['graphs']:
        ds = DataStream.objects.get(id = graphData['ds_id'])
        if key not in ds.can_read.all():
            ds.can_read.add(key)
        graph = SavedDSGraph(datastream = ds, start = start, end = end,
                             reduction_type = graphData['reduction'], granularity = gran,
                             zoom_start = start, zoom_end = end)
        graph.save()
        savedView.widget.add(graph)

    link = reverse('portcullis-saved-view', args = ['savedView', key.key])

    return HttpResponse(json.dumps({'html':'<a href="%s">%s</a>' % (link, link)}), mimetype='application/json')
    
