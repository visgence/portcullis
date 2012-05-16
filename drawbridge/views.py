from django.template import RequestContext
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.utils import simplejson
from django.shortcuts import render
from portcullis.models import DataStream, SensorReading, ScalingFunction 

def generate_view(request):
    return render(request,'display_nodes.html', context_instance=RequestContext(request))

def render_graph(request):
    if(request.method == 'GET'):
        start = int(request.GET.get('start'));
        end = int(request.GET.get('end'));
        datastream_id = int(request.GET.get('datastream_id'));
        granularity = request.GET.get('granularity');
        total_time = end - start
        stream_data = []

        if(granularity == None):
            granularity = 100;
    
        #Pull the data for this stream
        stream_info = DataStream.objects.get(id = datastream_id)

        #These fields could be used for graph settings client-side
        stream_info.xmin = start;
        stream_info.xmax = end;

        time_chunk = total_time / granularity
        end_of_chunk = start + time_chunk
        reduced_data = [];#will contain final data after it is reduced

        while (end_of_chunk < end):
            tmp_data=[];
            sub_readings = SensorReading.objects.filter(date_entered__gte = start, date_entered__lte = end_of_chunk, datastream = datastream_id).order_by('date_entered')
           
            if(sub_readings):
                tmp_data = reduce_data(sub_readings, start, end_of_chunk, stream_info.reduction_type)
            if(tmp_data):
                reduced_data.append(tmp_data)

            start = end_of_chunk
            end_of_chunk = start + time_chunk

        stream_info.data = reduced_data
        stream_info.label = stream_info.name

        json = to_json(stream_info)
        print json

        return HttpResponse(json)

        

def reduce_data(readings, start, end, reduction_type):
    coord_time = (end - start)/2 + start
    
    if(reduction_type == None or reduction_type == ""):
        reduction_type = 'mean'
    
    coord_data = mean(readings)
    return [coord_time, coord_data]

def mean(readings):
    summation = 0

    for record in readings:
        if(record.sensor_value != None):
            summation = summation + record.sensor_value

    return summation / len(readings)

def to_json(stream):
    stream_data = {"reduction_type":stream.reduction_type,"label":stream.name,"port_id":stream.port_id,"data":stream.data,"max_value":stream.max_value,"min_value":stream.min_value,"description":stream.description,"scaling_function":stream.description,"datastream_id":stream.id,"color":stream.color,"node_id":stream.node_id,"xmin":stream.xmin,"xmax":stream.xmax,"units":stream.units}

    return simplejson.dumps(stream_data)




