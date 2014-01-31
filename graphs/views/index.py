"""
" graphs/views/graphs_index.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#Django Imports
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext, Context

#Local Imports
from graphs.models import DataStream
from graphs.data_reduction import reductFunc

try:
    from default_graphs import DEFAULT_GRAPHS
except:
    DEFAULT_GRAPHS = []


def graphsIndex(request):

    graphs = []
    t_graph = loader.get_template('graph.html')
    reductions = reductFunc.keys()
    for graphId in DEFAULT_GRAPHS:
        
        try:
            stream = DataStream.objects.get(id=graphId)
        except DataStream.DoesNotExist:
            print "Invalid stream id %s given for default!" % str(graphId)
            continue

        c_graph = Context({
             'id': graphId
            ,'reduction': stream.reduction_type
            ,'reductions': reductions
        })
        graphs.append(t_graph.render(c_graph))
    
    t = loader.get_template('graphs.html') 
    c = RequestContext(request, {
        'graphs': graphs
        ,'defaultGraphs': DEFAULT_GRAPHS
    })
    return HttpResponse(t.render(c))
