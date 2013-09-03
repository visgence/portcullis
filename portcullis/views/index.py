"""
" portcullis/views/index.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

# System imports
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader, Context
from django.core.context_processors import csrf

# Local imports
from portcullis.views.side_pane import skeleton
from graphs.models import DataStream
from graphs.data_reduction import reductFunc

try:
    from default_graphs import DEFAULT_GRAPHS
except:
    DEFAULT_GRAPHS = []


def index(request, content = None, content_id = None):
    '''
    ' This is the main page index.  It should render all the
    ' place holders for the panes, as well as the initial content.
    '
    ' Keyword Args:
    '   content - The content page to render, passed by the url
    '   content-id - The identifier for the content, usually a key/token.
    '''

    if content == 'saved_view':
        side_pane = skeleton(request)
        content_pane = saved_view(request, content_id).content
    else:

        graphs = []
        t_graph = loader.get_template('graph.html')
        reductions = reductFunc.keys()
        for graphId in DEFAULT_GRAPHS:

            try:
                stream = DataStream.objects.get(id=graphId)
            except DataStream.DoesNotExist:
                raise Http404('Invalid stream id given for default!') 

            c_graph = Context({
                 'id': graphId
                ,'reduction': stream.reduction_type
                ,'reductions': reductions
            })
            graphs.append(t_graph.render(c_graph))

        content_t = loader.get_template('content_container.html')
        content_c = RequestContext(request, {
             'widgets': graphs
            ,'graphIds': DEFAULT_GRAPHS
            ,'defaultStreams': True
        }) 
        side_pane = skeleton(request)
        content_pane = content_t.render(content_c)

    nav_t = loader.get_template('nav_bar.html')
    nav_c = RequestContext(request, {})

    t = loader.get_template('main_page.html')
    c = RequestContext(request, { 'greeting': greeting(request),
                                  'side_pane': side_pane.content,
                                  'nav': nav_t.render(nav_c),
                                  'content_pane':content_pane
                                  })
    return HttpResponse(t.render(c), mimetype="text/html")


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


