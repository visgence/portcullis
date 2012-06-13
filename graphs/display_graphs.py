
from django.template import RequestContext
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.shortcuts import render
from portcullis.models import DataStream, SensorReading, ScalingFunction 
from check_access import check_access
from django.db.models import Q
import json

#Local Imports
import data_reduction

def display_graphs(request):
    '''
    Grabs all relevent data streams that are to be displayed and returns them to the display_nodes
    template. There are two ways for this to be called. The first is through the user portal after
    logging in.  This requires them to check off all streams they want to see and we grab them. 
    Otherwise we get url parameters through a GET and obtain the proper streams that way.

    TODO: The share this view linkage needs GET in order to work.  Would like to seperate that 
          functionality out to have POST as well from the user portal perhaps.  
    '''

    response = check_access(request)
    if(response):
        return response

    if(request.method == 'GET'):
        node = request.GET.get('node')
        port = request.GET.get('port')
        start = request.GET.get('start')
        end = request.GET.get('end')
        granularity = request.GET.get('granularity')
        show_public= request.GET.get('show_public')

        data = {
                    'granularity':granularity,
                    'start':start,
                    'end':end,
                    'streams':DataStream.objects.none()
               }
        
        if(granularity != None):
            data['granularity'] = int(granularity)

        if(request.GET.getlist('view')):
            for stream in request.GET.getlist('view'):
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        if(request.GET.getlist('owned')):
            for stream in request.GET.getlist('owned'):
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

        if(request.GET.getlist('public')):
            print request.GET.getlist('public')
            for stream in request.GET.getlist('public'):
                data['streams'] = data['streams'] | DataStream.objects.filter(id = stream) 

            #TODO Pull shared streams if the user requested them
        if(data['streams']):
            data['streams'] = data['streams'].order_by('node_id', 'port_id', 'id')
            return render(request,'display_nodes.html', data, context_instance=RequestContext(request))        

        #If a user passes a node param, pull all streams for that node
        if(node != None and port != None):
           data['streams'] = DataStream.objects.filter(node_id = int(node), port_id = int(port), users = request.user, permission__read = True).order_by('node_id', 'port_id', 'id')
        elif(node != None):
            data['streams'] = DataStream.objects.filter(node_id = int(node), users = request.user, permission__read = True).order_by('node_id', 'port_id', 'id')
        else:
            data['streams'] = DataStream.objects.filter(users = request.user, permission__read = True).order_by('node_id', 'port_id', 'id')

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
            granularity = 300
    
        #Pull the data for this stream
        stream_info = DataStream.objects.get(id = datastream_id)

        #These fields could be used for graph settings client-side
        stream_info.xmin = start
        stream_info.xmax = end


        #Check if there are less points in timeframe then granularity
        readings = SensorReading.objects.filter(date_entered__gte = start, date_entered__lte = end, datastream = datastream_id).order_by('date_entered')
        
        if(readings.count() < granularity):
            data = []

            #loop through and add all points to data
            for reading in readings:
                data.append([reading.date_entered,float("%.3f" % (reading.sensor_value))])

            stream_info.data = data
            stream_info.label = stream_info.name
            
            json = to_json(stream_info)
            #print "print json: %s" % json
            return HttpResponse(json)

        else:
            time_chunk = total_time / granularity
            #print "Time Chunk: %s" % time_chunk
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

            #print "stream_info: %s" % stream_info.data
            json = to_json(stream_info)
            #print "print json: %s" % json

            return HttpResponse(json)

        
def to_json(stream):

    min_value = stream.min_value
    if(min_value != None):
        min_value = float(min_value)

    max_value = stream.max_value
    if(max_value != None):
        max_value = float(max_value)



    stream_data = {"reduction_type":stream.reduction_type,"label":stream.name,"port_id":int(stream.port_id),"data":stream.data,"max_value":max_value,"min_value":min_value,"description":stream.description,"scaling_function":stream.scaling_function.id,"datastream_id":stream.id,"color":stream.color,"node_id":int(stream.node_id),"xmin":stream.xmin,"xmax":stream.xmax,"units":stream.units}

    return json.dumps(stream_data)




