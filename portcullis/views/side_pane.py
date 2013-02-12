#System Imports
from django.http import HttpResponse
from django.template import RequestContext, loader

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

    #Pull streams that are owned by this user.
    owned_streams = DataStream.objects.filter(owner__username = request.user.username).distinct()
        
    #Pull streams that are viewable by this user.
    viewable_streams = DataStream.objects.filter(can_read__owner__username = request.user.username).exclude(id__in=owned_streams).distinct()

    #Pull any public streams as well
    public_streams = DataStream.objects.filter(is_public = True).exclude(id__in=viewable_streams).exclude(id__in=owned_streams).distinct()

    t_streams = loader.get_template('user_streams.html')
    c_streams = RequestContext(request, {
            'user':request.user,
            'owned_streams':owned_streams,
            'public_streams':public_streams,
            'viewable_streams':viewable_streams
            })
    t_controls = loader.get_template('graph_controls.html')
    c_controls = RequestContext(request)
    
    return HttpResponse(t_controls.render(c_controls) + t_streams.render(c_streams), mimetype='text/html')


