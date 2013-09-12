"""
" portcullis/views/index.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

# System imports
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.context_processors import csrf

# Local imports
from portcullis.models import PortcullisUser as User
from check_access import check_access



def index(request):
    nav_t = loader.get_template('nav_bar.html')
    nav_c = RequestContext(request, {})

    t = loader.get_template('base.html')
    c = RequestContext(request, { 
        'greeting': greeting(request),
        'nav': nav_t.render(nav_c),
    })
    return HttpResponse(t.render(c), mimetype="text/html")


def utilitiesIndex(request):

    user = check_access(request)
    if not isinstance(user, User):
        return user 

    t = loader.get_template('utilities.html') 
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


def sensorsIndex(request):

    user = check_access(request)
    if not isinstance(user, User):
        return user 

    t = loader.get_template('sensors.html') 
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


#def index(request, content = None, content_id = None):
#    '''
#    ' This is the main page index.  It should render all the
#    ' place holders for the panes, as well as the initial content.
#    '
#    ' Keyword Args:
#    '   content - The content page to render, passed by the url
#    '   content-id - The identifier for the content, usually a key/token.
#    '''
#
#    graphs = []
#    t_graph = loader.get_template('graph.html')
#    reductions = reductFunc.keys()
#    for graphId in DEFAULT_GRAPHS:
#
#        try:
#            stream = DataStream.objects.get(id=graphId)
#        except DataStream.DoesNotExist:
#            raise Http404('Invalid stream id given for default!') 
#
#        c_graph = Context({
#             'id': graphId
#            ,'reduction': stream.reduction_type
#            ,'reductions': reductions
#        })
#        graphs.append(t_graph.render(c_graph))
#
#    g_container = loader.get_template('graph_container.html')
#    g_context = RequestContext(request, {'graphs': graphs})
#
#    s_template = loader.get_template('register_sensor.html')
#    s_context = RequestContext(request, {})
#
#    content_t = loader.get_template('content_container.html')
#    content_c = RequestContext(request, {
#         'widget': g_container.render(g_context)
#        ,'graphIds': DEFAULT_GRAPHS
#        ,'defaultStreams': True
#        ,'sensorTemplate': s_template.render(s_context)
#    }) 
#    side_pane = skeleton(request)
#    content_pane = content_t.render(content_c)
#
#    nav_t = loader.get_template('nav_bar.html')
#    nav_c = RequestContext(request, {})
#
#    t = loader.get_template('main_page.html')
#    c = RequestContext(request, { 'greeting': greeting(request),
#                                  'side_pane': side_pane.content,
#                                  'nav': nav_t.render(nav_c),
#                                  'content_pane':content_pane
#                                  })
#    return HttpResponse(t.render(c), mimetype="text/html")


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


