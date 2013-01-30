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

# Local imports
from portcullis.views.side_pane import streams
from portcullis.views.login import greeting

def index(request):
    '''
    ' This is the main page index.  It should render all the
    ' place holders for the panes, as well as the initial content.
    '''

    # For first iteration of this function, just render the side pane as the user_streams
    side_pane = streams(request)
    content_pane = ''

    t = loader.get_template('main_page.html')
    c = RequestContext(request, { 'greeting': greeting(request),
                                  'side_pane': side_pane.content,
                                 'content_pane':content_pane})
    return HttpResponse(t.render(c), mimetype="text/html")
