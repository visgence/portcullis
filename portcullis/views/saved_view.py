"""
" portcullis/views/saved_view.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


# System Imports
from django.http import HttpResponse, Http404
from django.template import RequestContext, Context, loader

# Local Imports
from portcullis.models import SavedView, Key
from graphs.data_reduction import reductFunc

def saved_view(request, token):
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

