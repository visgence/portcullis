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
            js = js + str(function.id) + ": function(x){" + str(function.definition) + "}, "
        js = js + "};"

        return HttpResponse(js,mimetype='application/javascript')

