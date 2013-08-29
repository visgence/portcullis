from django.http import HttpResponse
from graphs.models import ScalingFunction 

def scaling_functions(request):
    if(request.method == 'GET'):
        #Pull the data for this stream
        scaling_functions = ScalingFunction.objects.all()
        
        js = "scaling_functions = {"

        for function in scaling_functions:
            js = js + str(function.id) + ": function(x){" + str(function.definition) + "}, "
        js = js + "};"

        return HttpResponse(js,mimetype='application/javascript')

