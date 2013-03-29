"""
" portcullis/ajax.py
" Contributing Authors:
"    Evan Salazar   (Visgence, Inc)
"    Jeremiah Davis (Visgence, Inc)
"    Bretton Murphy (Visgence, Inc)
"
" (c) 2013 Visgence, Inc.
"""

# System Imports
from dajaxice.decorators import dajaxice_register
from django.http import HttpResponse
from django.template import Context, loader
from collections import OrderedDict
from django.contrib.auth import get_user_model
AuthUser = get_user_model()

# Local imports
from portcullis.models import DataStream
from check_access import check_access

try:
    import simplejson as json
except ImportError:
    import json


@dajaxice_register
def stream_subtree(request, name, group):
    '''
    ' This function will take a partial datastream name, delimited
    ' with '|' and return the next level of the subtree
    ' that matches.
    '
    ' Keyword Args:
    '    name - The 'path' of the subtree (beggining of the name of
    '           the items interested in.)
    '    group - The group to get the subtree for.  Is this a public
    '            group, or an owned group or a
    '            viewable group.
    '''

    portcullisUser = check_access(request)
    if isinstance(portcullisUser, HttpResponse):
        return portcullisUser.content

    # Check that we are logged in before trying to filter the streams
    if isinstance(portcullisUser, AuthUser):
        if group == 'owned':
            streams = DataStream.objects.filter(name__startswith=name)
            streams = streams.filter(owner=portcullisUser)
        elif group == 'viewable':
            streams = DataStream.objects.get_viewable(portcullisUser)
            streams = streams.filter(name__startswith=name)
            streams = streams.exclude(owner=portcullisUser)
        elif group == 'public':
            streams = DataStream.objects.filter(name__startswith=name)
            viewableStreams = DataStream.objects.get_viewable(portcullisUser)
            streams = streams.filter(is_public=True).exclude(owner=portcullisUser)
            streams = streams.exclude(id__in=viewableStreams)
        else:
            return json.dumps({'errors': 'Error: %s is not a valid datastream type.' % group})

    elif group == 'public':
        streams = DataStream.objects.filter(name__startswith=name)
        streams = streams.filter(is_public=True)
    else:
        return json.dumps({'errors': 'Error: You must be logged in to see the %s datastream type.' % group})

    level = name.count('|')
    nodes = []
    leaves = {}

    for s in streams:
        split_name = s.name.split('|')
        n_name = split_name[level]

        # Is this a node or leaf?
        if len(split_name) > level + 1:
            if (n_name) not in nodes:
                nodes.append(n_name)
        elif n_name not in leaves:
            leaves[n_name] = s.id
        else:
            return json.dumps({'errors': 'Duplicate name in Database!'})

    t = loader.get_template('stream_subtree.html')
    nodes.sort()
    leaves = OrderedDict(sorted(leaves.items(), key=lambda t: t[0]))
    c = Context({
            'nodes':  nodes,
            'leaves': leaves,
            'path':   name,
            'group':  group
            })
    return json.dumps({'html': t.render(c)})
