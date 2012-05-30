from django.template import RequestContext
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.utils import simplejson
from django.shortcuts import render
from portcullis.models import DataStream, SensorReading, ScalingFunction 
from check_access import check_access

#Local Imports
import data_reduction

def display_graphs(request):

    response = check_access(request)
    print response
    if(response):
        return response

    if(request.method == 'GET'):
        node = request.GET.get('node')
        port = request.GET.get('port')
        start = request.GET.get('start')
        end = request.GET.get('end')
        granularity = request.GET.get('granularity')

        streams = 0
        data = {
                    'granularity':granularity,
                    'start':start,
                    'end':end
               }

        if(granularity != None):
            data['granularity'] = int(granularity)

        if(node != None and port != None):
            data['streams'] = DataStream.objects.filter(node_id = int(node), port_id = int(port))
        elif(node != None):
            data['streams'] = DataStream.objects.filter(node_id = int(node))
        else:
            data['streams'] = DataStream.objects.all()

        return render(request,'display_nodes.html', data, context_instance=RequestContext(request))        







##
#Takes a single datastream id and a time frame and generates json for the data
#Returns: json
##
def render_graph(request):
    if(request.method == 'GET'):
        start = int(request.GET.get('start'))
        end = int(request.GET.get('end'))
        datastream_id = int(request.GET.get('datastream_id'))
        granularity = int(request.GET.get('granularity'))
        total_time = end - start
        stream_data = []

        if(granularity == None):
            granularity = 100
    
        #Pull the data for this stream
        stream_info = DataStream.objects.get(id = datastream_id)

        #These fields could be used for graph settings client-side
        stream_info.xmin = start
        stream_info.xmax = end

        time_chunk = total_time / granularity
        end_of_chunk = start + time_chunk
        reduced_data = []#will contain final data after it is reduced

        while (end_of_chunk < end):
            tmp_data=[]
            sub_readings = SensorReading.objects.filter(date_entered__gte = start, date_entered__lte = end_of_chunk, datastream = datastream_id).order_by('date_entered')
           
            if(sub_readings):
                tmp_data = data_reduction.reduce_data(sub_readings, start, end_of_chunk, stream_info.reduction_type)
            if(tmp_data):
                reduced_data.append(tmp_data)

            start = end_of_chunk
            end_of_chunk = start + time_chunk

        stream_info.data = reduced_data
        stream_info.label = stream_info.name

        json = to_json(stream_info)
        print "print scaling_function: %s" % stream_info.scaling_function
        print "print json: %s" % json

        return HttpResponse(json)

        
def to_json(stream):
    stream_data = {"reduction_type":stream.reduction_type,"label":stream.name,"port_id":stream.port_id,"data":stream.data,"max_value":stream.max_value,"min_value":stream.min_value,"description":stream.description,"scaling_function":stream.scaling_function.id,"datastream_id":stream.id,"color":stream.color,"node_id":stream.node_id,"xmin":stream.xmin,"xmax":stream.xmax,"units":stream.units}

    return simplejson.dumps(stream_data)




