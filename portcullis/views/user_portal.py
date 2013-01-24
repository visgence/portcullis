#System Imports
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.context_processors import csrf

#Local Imports
from portcullis.models import DataStream
from check_access import check_access

def user_streams(request):
    '''
    Grab all relevent streams to display as checkboxes in the user portal.  We make sure to remove any duplicate streams from each various section.
    Presedence is given to owner, then to readable, then to public for the duplicate removal.
    '''

    response = check_access(request)
    if(response):
        return response

    if request.method == 'GET':
        #Pull streams that are owned by this user.
        owned_streams = DataStream.objects.filter(owner__username = request.user.username) 
        
        #Pull streams that are viewable by this user.
        viewable_streams = DataStream.objects.filter(can_read__owner__username = request.user.username).exclude(id__in=owned_streams)

        #Pull any public streams as well
        public_streams = DataStream.objects.filter(is_public = True).exclude(id__in=viewable_streams).exclude(id__in=owned_streams)


        streams_page = loader.get_template('user_streams.html')
        streams_context = RequestContext(request, {'user':request.user,'owned_streams':owned_streams, 'public_streams':public_streams,'viewable_streams':viewable_streams})
        streams_context.update(csrf(request))

        main_page = loader.get_template('main_page.html')
        main_context = RequestContext(request, {'side_pane': streams_page.render(streams_context)})

        return HttpResponse(main_page.render(main_context))


