from models import DataStream
from django.http import HttpResponse
from django.template import Context, loader
from django.core.context_processors import csrf
from check_access import check_access

def user_streams(request):

    response = check_access(request)
    if(response):
        return response

    if request.method == 'GET':
        streams = DataStream.objects.filter(owner = request.user)

        t = loader.get_template('user_streams.html')
        c = Context({'user':request.user,'streams':streams})
        c.update(csrf(request))
        return HttpResponse(t.render(c))


