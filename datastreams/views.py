from django.template import RequestContext
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.utils import simplejson
from django.shortcuts import render
from portcullis.models import DataStream, SensorReading, ScalingFunction 
from check_access import check_access
from django.db.models import Q

def csv(request):

    response = check_access(request)
    if(response):
        return response

    if(request.method == 'GET'):
        stream_id = request.GET.get('data_stream')
        start = request.GET.get('start')
        end = request.GET.get('end')

        if(start is None):
            #TODO display error message
            return render(request,'csv.html', context_instance=RequestContext(request))        

        if(end is None):
            #TODO display error message
            return render(request,'csv.html', context_instance=RequestContext(request))        

        data_stream = DataStream.objects.get(id = stream_id)

        readings = SensorReading.objects.filter(timestamp__gte = start, timestamp__lte = end, datastream = data_stream).order_by('timestamp')


        data = {
                    'start':start,
                    'end':end,
                    'data_stream':data_stream,
                    'readings':readings
               }
        
        return render(request,'csv.html', data, context_instance=RequestContext(request))        

