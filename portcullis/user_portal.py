from models import DataStream, UserPermission
from django.http import HttpResponse
from django.template import Context, loader
from django.core.context_processors import csrf
from check_access import check_access

def user_streams(request):

    response = check_access(request)
    if(response):
        return response

    if request.method == 'GET':
        #Pull streams that are owned by this user.
        owned_streams = DataStream.objects.filter(userpermission__user = request.user, userpermission__owner = True) 
        
        #Pull streams that are viewable by this user.
        viewable_streams = DataStream.objects.filter(userpermission__user = request.user, userpermission__read = True).exclude(id__in=owned_streams)

        #Pull any public streams as well
        public_streams = DataStream.objects.filter(is_public = True).exclude(id__in=viewable_streams).exclude(id__in=owned_streams)


        t = loader.get_template('user_streams.html')
        c = Context({'user':request.user,'owned_streams':owned_streams, 'public_streams':public_streams,'viewable_streams':viewable_streams})
        c.update(csrf(request))
        return HttpResponse(t.render(c))


