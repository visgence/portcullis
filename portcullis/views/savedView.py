"""
" portcullis/views/savedView.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


# System Imports
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.template import RequestContext, Context, loader
from django.views.decorators.http import require_POST
from django.utils import timezone
try: import simplejson as json
except ImportError: import json
from datetime import datetime, timedelta

# Local Imports
from portcullis.models import SavedView, Key, DataStream, PortcullisUser
from graphs.models import SavedDSGraph
from graphs.data_reduction import reductFunc
from check_access import check_access

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

    reductions = reductFunc.keys()
    graphs = []
    t_graph = loader.get_template('graph.html')
    for w in view.widget.all():
        c_graph = Context({
                'id': w.saveddsgraph.datastream.id,
                'node_id': w.saveddsgraph.datastream.node_id,
                'port_id': w.saveddsgraph.datastream.port_id,
                'reductions': reductions,
                'widget_id': w.id
                })
        graphs.append(t_graph.render(c_graph))

    t = loader.get_template('content_container.html')
    c = RequestContext(request, {
                                    'widgets': graphs,
                                    'token': token,
                                 })

    return HttpResponse(t.render(c))

@transaction.commit_manually
@require_POST
def createSavedView(request):
    '''
    ' Create a savedView and return the token or link for that shared view.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        transaction.rollback()
        return portcullisUser
    if request.user.is_anonymous():
        transaction.rollback()
        # TODO: Should not be a return, should be a raise, but don't have a 403 right now,
        #But should be okay, because save has not been called yet.
        return HttpResponseForbidden('Must be logged in to create saved view')

    if 'jsonData' not in request.POST:
        transaction.rollback()
        raise Http404('Unrecognized data')

    try:
        jsonData = json.loads(request.POST['jsonData'])
    except Exception as e:
        transaction.rollback()
        return HttpResponse(json.dumps({'errors': 'Ivalid json: %s' % e.message}, mimetype="application/json"))

    expires = timezone.now() + timedelta(days=7)
    key = Key.objects.generateKey(portcullisUser, 'Saved view', expires, 20)

    # Create a SavedView object and graphs, and save data.
    savedView = SavedView.objects.create(key = key)

    try:
        start = jsonData['start']
        end = jsonData['end']
        gran = jsonData['granularity']
    except Exception as e:
        transaction.rollback()
        message = 'Error getting json data: %s: %s:' % (type(e), e.message)
        return HttpResponse(json.dumps({'errors': message}), mimetype="application/json")

    for graphData in jsonData['graphs']:
        try:
            ds = DataStream.objects.get(id = graphData['ds_id'])
        except DataStream.DoesNotExist:
            transaction.rollback()
            return HttpResponse(json.dumps({'errors': 'Datastream does not exist.'}), mimetype="application/json")
        except Exception as e:
            transaction.rollback()
            return HttpResponse(json.dumps(
                    {'errors': 'Unknown error occurred: %s: %s' % (type(e), e.message)},
                    mimetype="application/json"))
                               
        # Make sure not to add the key if not the owner.
        if key not in ds.can_read.all() and portcullisUser == ds.owner and not ds.is_public:
            ds.can_read.add(key)
                               
        try:
            reduction = graphData['reduction']
            zoom_start = graphData['zoom_start']
            zoom_end = graphData['zoom_end']
        except Exception as e:
            transaction.rollback()
            message = 'Error getting json data for datastream %d: %s' % (ds.id, e.message)
            return HttpResponse(json.dumps({'errors': message}), mimetype='application/json')
        
        graph = SavedDSGraph(datastream = ds, start = start, end = end,
                             reduction_type = graphData['reduction'], granularity = gran,
                             zoom_start = zoom_start, zoom_end = zoom_end)
        try:
            graph.save()
            savedView.widget.add(graph)
        except Exception as e:
            transaction.rollback()
            return HttpResponse(json.dumps({'errors': 'Error saving graph: %s' % e.message}),mimetype='application/json')
        
    link = reverse('portcullis-saved-view', args = ['savedView', key.key])

    transaction.commit()
    
    return HttpResponse(json.dumps({'html':'<a href="%s">%s</a>' % (link, link)}), mimetype='application/json')
    
