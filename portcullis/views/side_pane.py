#System Imports
from django.http import HttpResponse
from django.template import Context, RequestContext, loader
from collections import OrderedDict
from django.contrib.auth import get_user_model
AuthUser = get_user_model()
try:
    import simplejson as json
except ImportError:
    import json

#Local Imports
from portcullis.models import DataStream, Device
from check_access import check_access

def skeleton(request):
    '''
    Render the side_pane skeleton.  The other stuff will be loaded in later with ajax.
    '''

    user = check_access(request)
    logged_in = True
    if user is None or isinstance(user, HttpResponse):
        logged_in = False


    t = loader.get_template('side_pane.html')
    c = RequestContext(request, {
            'streams': streams(request).content,
            'logged_in': logged_in
            })
    return HttpResponse(t.render(c), mimetype='text/html')

def streams(request):
    '''
    Grab all relevent streams to display as checkboxes in the user portal.  We make sure to remove any duplicate streams from each various section.
    Presedence is given to owner, then to readable, then to public for the duplicate removal.
    '''

    user = check_access(request)

    if isinstance(user, HttpResponse):
        return user

    t_subtree = loader.get_template('stream_subtree.html')

    #Only get owned and viewable streams if we have a logged in User
    owned_streams = []
    viewable_streams = []
    owned_subtree = None
    viewable_subtree = None
    if user is not None:
        #Pull streams that are owned by this user.
        owned_devices = Device.objects.filter(owner=user)
        owned_streams = DataStream.objects.filter(device__in=owned_devices)
        c_dict = stream_tree_top(owned_streams)
        c_dict.update({'group':'owned'})
        owned_subtree = t_subtree.render(Context(c_dict))

        #Pull streams that are viewable by this user.
        viewable_streams = DataStream.objects.get_viewable(user).exclude(id__in=owned_streams).distinct()
        c_dict = stream_tree_top(viewable_streams)
        c_dict.update({'group':'viewable'})
        viewable_subtree = t_subtree.render(Context(c_dict))

    #Pull any public streams as well
    #public_streams = DataStream.objects.filter(is_public = True).exclude(id__in=viewable_streams).exclude(id__in=owned_streams).distinct()
    #c_dict = stream_tree_top(public_streams)
    #c_dict.update({'group':'public'})
    #public_subtree = t_subtree.render(Context(c_dict))

    t_streams = loader.get_template('user_streams.html')
    c_streams = RequestContext(request, {
            'user':request.user,
            'owned_streams': owned_streams,
            'viewable_streams': viewable_streams,
            #'public_streams': public_streams,
            'owned_subtree': owned_subtree,
            #'public_subtree': public_subtree,
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
    nodes = {}
    leaves = {}
    for s in streams:
        # Assume for now that names are unique.
        # TODO: Validate (in save/models, etc.) that no 2 objects can have names such that name and name::other
        #  exist.
        spart = s.name.partition('|')
        if spart[2] != '':
            if spart[0] not in nodes:
                nodes[spart[0]] = None
        else:
            leaves[spart[0]] = s.id

    nodes = OrderedDict(sorted(nodes.iteritems(), key = lambda t: t[0]))
    leaves = OrderedDict(sorted(leaves.iteritems(), key = lambda t: t[0]))
    return {'nodes': nodes, 'leaves': leaves}



def stream_subtree(request):
    '''
    ' This function will take a partial datastream name, delimited
    ' with '|' and return the next level of the subtree
    ' that matches.
    '''

    portcullisUser = check_access(request)
    if isinstance(portcullisUser, HttpResponse):
        dump = json.dumps({'access_error': 'Sorry, but you are not logged in.'})
        return HttpResponse(dump, content_type="application/json")

    try:
        jsonData = json.loads(request.GET.get('jsonData'))
    except:
        dump = json.dumps({'errors': 'Error getting json data'})
        return HttpResponse(dump, content_type="application/json")

    name = jsonData['name']
    group = jsonData['group']

    # Check that we are logged in before trying to filter the streams
    if isinstance(portcullisUser, AuthUser):
        if group == 'owned':
            streams = DataStream.objects.filter(name__startswith=name)
            streams = streams.filter(owner=portcullisUser)
        elif group == 'viewable':
            streams = DataStream.objects.get_viewable(portcullisUser)
            streams = streams.filter(name__startswith=name)
            streams = streams.exclude(owner=portcullisUser)
        #elif group == 'public':
        #    streams = DataStream.objects.filter(name__startswith=name)
        #    viewableStreams = DataStream.objects.get_viewable(portcullisUser)
        #    streams = streams.filter(is_public=True).exclude(owner=portcullisUser)
        #    streams = streams.exclude(id__in=viewableStreams)
        else:
            dump = json.dumps({'errors': 'Error: %s is not a valid datastream type.' % group})
            return HttpResponse(dump, content_type="application/json")

    #elif group == 'public':
    #    streams = DataStream.objects.filter(name__startswith=name)
    #    streams = streams.filter(is_public=True)
    else:
        dump = json.dumps({'errors': 'Error: You must be logged in to see the %s datastream type.' % group})
        return HttpResponse(dump, content_type="application/json")

    level = name.count('|')
    nodes = {}
    leaves = {}

    for s in streams:
        split_name = s.name.split('|')
        n_name = split_name[level]

        # Is this a node or leaf?
        if len(split_name) > level + 1:
            if (n_name) not in nodes:
                nodes[n_name] = None
        elif n_name not in leaves:
            leaves[n_name] = s.id
        else:
            dump = json.dumps({'errors': 'Duplicate name in Database!'})
            return HttpResponse(dump, content_type="application/json")

    t = loader.get_template('stream_subtree.html')
    nodes = OrderedDict(sorted(nodes.iteritems(), key=lambda t: t[0]))
    leaves = OrderedDict(sorted(leaves.iteritems(), key=lambda t: t[0]))
    c = Context({
            'nodes':  nodes,
            'leaves': leaves,
            'path':   name,
            'group':  group
            })
    return HttpResponse(json.dumps({'html': t.render(c)}), content_type="application/json")








