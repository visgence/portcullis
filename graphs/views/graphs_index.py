"""
" graphs/views/graphs_index.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#Django Imports
from django.http import HttpResponse
from django.template import loader, RequestContext



def graphsIndex(request):

    t = loader.get_template('graphs.html') 
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))
