#System Imports
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.decorators.http import require_GET
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from portcullis.models import DataStream, Key
from check_access import check_access
from graphs.data_reduction import reductFunc
from settings import DOMAIN

def display_simple_base(request):

    t = loader.get_template('base_simple.html')
    c = RequestContext(request, {
            'DOMAIN': DOMAIN,
            'start': request.GET['start'], 
            'end': request.GET['end'],
            'streams': request.GET['streams'],
            'token': request.GET.get('token', '')
            })

    resp = HttpResponse(t.render(c), mimetype='text/html')
    resp['Access-Control-Allow-Origin'] = '*'
    return resp

def display_simple_graph(request):
    json_data = json.loads(request.GET['json_data'])

    try:
        stream = DataStream.objects.get(id = int(json_data['stream']))
    except ObjectDoesNotExist:
        raise Http404()

    perm = True
    if not stream.is_public:
        token = json_data['token']
        
        try:
            key = Key.objects.get(key = token)
            if not key.isCurrent() or key not in stream.can_read.all():
                perm = False
        except Key.DoesNotExist:
            perm = False

    reductions = reductFunc.keys()    
    t_graph = loader.get_template('graph.html')
    c_graph = Context({
        'id':         stream.id,
        'reduction':  stream.reduction_type,
        'reductions': reductions,
        'permission': perm
    })
    r_graph = t_graph.render(c_graph)

    return HttpResponse(json.dumps({'graph': r_graph, "perm": perm}), mimetype="application/json")

@require_GET
def display_graph(request):
    '''
    ' Use JSON data to retrieve the appropriate datastream for rendering.
    '''
    
    user = check_access(request)
    if isinstance(user, HttpResponse):
        return user.content
    
    json_data = json.loads(request.GET['json_data'])

    try:
        stream = DataStream.objects.get(id = int(json_data['stream']))
        if not stream.can_view(user):
            raise Http404("Sorry, but you do not have permission to view this graph.")
    except ObjectDoesNotExist:
        raise Http404()

    reductions = reductFunc.keys()    
    t_graph = loader.get_template('graph.html')
    c_graph = Context({
        'id': stream.id,
        'reduction': stream.reduction_type,
        'reductions': reductions
    })

    return HttpResponse(t_graph.render(c_graph), mimetype="text/html")


def render_graph_container(request):
    '''
    ' Renders and returns just the graph container as html.
    '''

    t_graph_contain = loader.get_template('graph_container.html')
    c_graph_contain = RequestContext(request, {})
    return HttpResponse(t_graph_contain.render(c_graph_contain), mimetype="text/html")

def plotter(request):
    '''
    ' This view returns plotter.js rendered with absolute urls.
    '''
    t = loader.get_template('plotter.js')
    c = RequestContext(request, {
            'DOMAIN': DOMAIN
            })
    resp = HttpResponse(t.render(c), mimetype='text/javascript')
    resp['Access-Control-Allow-Origin'] = '*'
    return resp
