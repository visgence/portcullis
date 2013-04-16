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
from portcullis.views.side_pane import skeleton
from portcullis.views.login import greeting
from portcullis.views.saved_view import saved_view

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
        content_t = loader.get_template('content_container.html')
        content_c = RequestContext(request, {}) 
        side_pane = skeleton(request)
        content_pane = content_t.render(content_c)

    t = loader.get_template('main_page.html')
    c = RequestContext(request, { 'greeting': greeting(request),
                                  'side_pane': side_pane.content,
                                  'content_pane':content_pane
                                  })
    return HttpResponse(t.render(c), mimetype="text/html")
