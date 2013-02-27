#System Imports
from django.http import HttpResponse
from django.template import Context, RequestContext, loader
from collections import OrderedDict

#Local Imports
from portcullis.models import DataStream
from check_access import check_access

def streams(request):
    '''
    Grab all relevent streams to display as checkboxes in the user portal.  We make sure to remove any duplicate streams from each various section.
    Presedence is given to owner, then to readable, then to public for the duplicate removal.
    '''

    # Already filters what is available by username, so don't need to explicitly check access here.
    #response = check_access(request)
    #if(response):
    #    return response

    t_subtree = loader.get_template('stream_subtree.html')

    #Pull streams that are owned by this user.
    owned_streams = DataStream.objects.filter(owner__username = request.user.username).distinct()
    owned_subtree = t_subtree.render(Context(stream_tree_top(owned_streams)))

    #Pull streams that are viewable by this user.
    viewable_streams = DataStream.objects.filter(can_read__owner__username = request.user.username).exclude(id__in=owned_streams).distinct()
    viewable_subtree = t_subtree.render(Context(stream_tree_top(viewable_streams)))

    #Pull any public streams as well
    public_streams = DataStream.objects.filter(is_public = True).exclude(id__in=viewable_streams).exclude(id__in=owned_streams).distinct()
    public_subtree = t_subtree.render(Context(stream_tree_top(public_streams)))

    t_streams = loader.get_template('user_streams.html')
    c_streams = RequestContext(request, {
            'user':request.user,
            'owned_streams': owned_streams,
            'viewable_streams': viewable_streams,
            'public_streams': public_streams,
            'owned_subtree': owned_subtree,
            'public_subtree': public_subtree,
            'viewable_subtree': viewable_subtree
            })
    t_controls = loader.get_template('graph_controls.html')
    c_controls = RequestContext(request)
    
    return HttpResponse(t_controls.render(c_controls) + t_streams.render(c_streams), mimetype='text/html')


def stream_tree_top(streams):
    '''
    ' This function should create the top level tree structure for the datastreams, and return it as a dictionary.
    ' Only the keys should really be necessary, though.
    '
    ' Keyword Args:
    '    streams - An iterable of datastreams.
    '
    ' Returns:
    '    A dictionary containing the top level of the tree as strings.  The values are True for nodes, and
    '    False for leaves.
    '''
    nodes = []
    leaves = {}
    for s in streams:
        # Assume for now that names are unique.
        # TODO: Validate (in save/models, etc.) that no 2 objects can have names such that name and name::other
        #  exist.
        spart = s.name.partition('|')
        if spart[2] != '':
            if spart[0] not in nodes:
                nodes.append(spart[0])
        else:
            leaves[spart[0]] = s.id

    nodes.sort()

    return {'nodes': nodes, 'leaves': OrderedDict(sorted(leaves.items(), key = lambda t: t[0]))}



