"""
" portcullis/views/signup.py
" Contributing Authors:
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

#Django Imports
from django.http import HttpResponse
from django.template import loader, RequestContext


def signupPage(request):

    t = loader.get_template('signup_page.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))
