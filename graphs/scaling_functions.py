from django.template import RequestContext
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.utils import simplejson
from django.shortcuts import render
from portcullis.models import ScalingFunction 

def scaling_functions(request):
    if(request.method == 'GET'):
        #Pull the data for this stream
        scaling_functions = ScalingFunction.objects.all()
        
        js = "scaling_functions = {"

        for function in scaling_functions:
            js = js + str(function.function_id) + ": function(x){" + str(function.definition) + "}, "
        js = js + "};"
        print scaling_functions
        #json = to_json(stream_info)
        #print json

        return HttpResponse(js)

        
def to_json(stream):
    stream_data = {"reduction_type":stream.reduction_type,"label":stream.name,"port_id":stream.port_id,"data":stream.data,"max_value":stream.max_value,"min_value":stream.min_value,"description":stream.description,"scaling_function":stream.description,"datastream_id":stream.id,"color":stream.color,"node_id":stream.node_id,"xmin":stream.xmin,"xmax":stream.xmax,"units":stream.units}

    return simplejson.dumps(stream_data)




