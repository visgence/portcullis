/**
*
*plotter.js
*
*script: This script has two primary functions. First, to retrieve all correctly formatted
*portcullis-graph divs from a page. Secondly, to query for data for the datastream ids.
*
**/

// Returns plot select event handler  for binding

//global
var timezone_date = new Date();
var timezone_offset = timezone_date.getTimezoneOffset()*60*1000//milliseconds
var overviewPlots = {};

function create_plot_select_handler(datastream_id) 
{ 
    return function(event,ranges) 
    { 
        if($("#zoom_sync_"+datastream_id).is(':checked'))         
            zoom_all_graphs(ranges);
        else
            zoom_graph(ranges, datastream_id);
        var start = new Date(ranges.xaxis.from + timezone_offset);
        var end= new Date(ranges.xaxis.to + timezone_offset);

        update_link();
    } 
}//end create_plot_select_handler

//On load function will search for any 'portcullis-graph' divs on the page.
$("document").ready(function ()
{
    var d = new Date();
    var range = (48 * 60 * 60);    
    var epoch_start;
    var epoch_end;
    var start = new Date($("#start").val());
    var end = new Date($("#end").val());

    //check for start/end time from server
    if(!$("#start").val() && !$("#end").val())
    {    
        start = new Date(d.getTime() - range*1000);
        end= new Date(d.getTime());
 
        //display to user in localtime
        $("#start").val(start.toLocaleString());
        $("#end").val(end.toLocaleString());
    }
    else if($("#start").val() && !$("#end").val())
    {
        start = new Date($("#start").val());
        end= d.getTime();  
        d= new Date(end);
        $("#end").val(d.toLocaleString());
    }

    epoch_start = start.getTime() - timezone_offset;
    epoch_end = end.getTime() - timezone_offset;
    
    //check for granularity from server
    if(!$("#granularity").val()) 
    {
        $("#granularity").val(300);//default
    }
 
    //Find all portcullis graph divs
    divs = $(".portcullis-graph");

    //bind each one
    for (var i = 0; i < divs.length; i++) 
    {
        var datastream_id = divs[i].id;

        //bind main graphs
        $("#sensor" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));
        
        //bind  overview graph 
        $("#overview" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));
    }//end for

    //Creating range object for query
    var ranges = { xaxis: { from: epoch_start, to: epoch_end }};
    loadAllGraphs(ranges);    
    update_link();
});//end on_load

// scale incoming data
function scale_data(data)
{
    for(var i=0;i<data.data.length;i++) 
    {
        data.data[i][0] = data.data[i][0]*1000 - timezone_offset;//converting seconds to milliseconds
        data.data[i][1] = scaling_functions[data.scaling_function](data.data[i][1]) 
    }
    return data;
}

/*Plots a  graph.
* returns: plot object
*/
function plot_graph(data,options,div)
{
 
    if(data.permission == "false")
    {
        var empty_plot = $.plot($(div), [[2,2]], 
                        {
                            bars: { show: true, barWidth: 0.5, fill: 0.9 },
                            label:  data.label, 
                            xaxis: {ticks: [], autoscaleMargin: 0.02, min: 0, max: 10 },
                            yaxis: { min: 0, max: 10 }
                        });
        //inform the user that there is no data for this sensor 
        var offset = empty_plot.pointOffset({ x: 4, y: 5});
        $(div).append('<div style="position:absolute;width:800px;text-align:center;top:' + offset.top + 
                      'px;color:#666;font-size:smaller">You do not have permission to view '+ data.label + '</div>');

    }
    //If no data then say so inside empty graph
    else if(data.data.length==0)
    {  
        var empty_plot = $.plot($(div), [[2,2]], 
                        {
                            bars: { show: true, barWidth: 0.5, fill: 0.9 },
                            label:  data.label, 
                            xaxis: {ticks: [], autoscaleMargin: 0.02, min: 0, max: 10 },
                            yaxis: { min: 0, max: 10 }
                        });
        //inform the user that there is no data for this sensor 
        var offset = empty_plot.pointOffset({ x: 4, y: 5});
        $(div).append('<div style="position:absolute;width:800px;text-align:center;top:' + offset.top + 
                      'px;color:#666;font-size:smaller">No Data for '+ data.label + ' in this range</div>');

        $('#datapoints_'+data.datastream_id).text('0');
        $('#actual_datapoints_'+data.datastream_id).text('0');
    } 
    else
    {
        var scaled_data = scale_data(data);
        var csv="time,raw reading,scaled value\n";
        for (var i in scaled_data['data'])
        {   
            //console.log(scaled_data['data'][i]);//DEBUG
            csv += data['data'][i][0]+",";
            csv += data['data'][i][1]+",";
            csv += scaled_data['data'][i][1]+"\n";
        }   

        scaled_data['raw_data'] = data['data'];
        var plot = $.plot($(div), [scaled_data], options);
        $(div+"_csv").html(csv);
        $('#datapoints_'+data.datastream_id).text(data.num_readings);
        $('#actual_datapoints_'+data.datastream_id).text(scaled_data['data'].length);
        return plot;
    }
}//end plot_graph

//queries for a time range(datepicker)
function submit_form(datastream_id)
{   
    var start = new Date($("#start").val());
    var end = new Date($("#end").val());
    
    if($("#granularity").val() == '')
        $("#granularity").val(300) 

    epoch_start = start.getTime();
    epoch_end= end.getTime();  
    
    epoch_start -= timezone_offset;
    epoch_end -= timezone_offset;

    var ranges = { xaxis: { from: epoch_start , to: epoch_end }};
    loadAllGraphs(ranges);
    update_link();
}//end submit_form

/*queries for data for a single datastream and a specific time period
 * ranges: date range for the query
 * granularity: how many data points the result should aim for
*/
function zoom_graph(ranges, datastream_id)
{
    var result = $.Deferred();
    var options = 
    { 
        lines: { show: true }, 
        xaxis: 
        {     
            mode: "time", 
            timeformat: " %m-%d %h:%M %p",
            min: ranges.xaxis.from,
            max: ranges.xaxis.to,
            ticks: 5
        },
        selection: {mode: "x"}
    };

    //plot the data that we receive
    function on_data_recieved(data) 
    {
        //set the graphs title
        $("#graph_title" + datastream_id).text(data.label + " - Node " + data.node_id + " - Stream " + datastream_id );
        overviewPlots[datastream_id].setSelection({xaxis: {from: ranges.xaxis.from, to: ranges.xaxis.to}}, true);
        options.yaxis = {min:data.min_value, max:data.max_value, axisLabel: data.units};
        var plot =  plot_graph(data,options,"#sensor" + datastream_id);
        result.resolve(plot);//sent back for binding
    }//end on data_recieved

    //request data for the new timeframe
    $.ajax(    
    {
        url:"/render_graph/?json=true&start=" + Math.round(ranges.xaxis.from/1000 + timezone_offset/1000 )  + 
                                      "&end=" + Math.round(ranges.xaxis.to/1000 + timezone_offset/1000) + 
                              "&granularity=" + $("#granularity").val() + 
                            "&datastream_id=" + datastream_id,
        method: 'GET',
        dataType: 'json',
        success: on_data_recieved
    });

    return result;
}//end zoom_graph

function loadAllGraphs(ranges)
{
    divs = $(".portcullis-graph");
    var granularity = $("#granularity").val();

    //Cycle though all graphs and fetch data from server
    for (var i = 0; i < divs.length; i++) 
    {
        var datastream_id = divs[i].id;
        $.ajax(    
        {
            url:"/render_graph/?json=true&start=" + Math.round(ranges.xaxis.from/1000 + timezone_offset/1000) + 
                                          "&end=" + Math.round(ranges.xaxis.to/1000 + timezone_offset/1000) + 
                                  "&granularity=" + granularity + 
                                "&datastream_id=" + datastream_id,
            method: 'GET',
            dataType: 'json',
            success: function(data) {

                //Make a full copy of the data since the two graphs need their own copy to work.
                var dData = $.extend(true, {}, data);
                renderGraph(data, ranges, true);
                renderOverview(dData, ranges);
            }
        });
    }
}

function renderGraph(data, ranges, shouldScale)
{
    var result = $.Deferred();
    var dataStreamId = data.datastream_id;
    var options = 
    { 
        lines: { show: true }, 
        xaxis: 
        {     
            mode: "time", 
            timeformat: " %m-%d %h:%M %p",
            min: ranges.xaxis.from,
            max: ranges.xaxis.to,
            ticks: 5
        },
        selection: {mode: "x"}
    };
    
    //set the graphs title
    $("#graph_title" + dataStreamId).text(data.label);
    options.yaxis = {min:data.min_value, max:data.max_value, axisLabel: data.units};
    var plot;
    if(shouldScale)
        plot = plot_graph(data,options,"#sensor" + dataStreamId);
    else
    {
        plot = $.plot($("#sensor" + dataStreamId), [data], options);
        console.log(data);
        $('#datapoints_'+dataStreamId).text(data.num_readings);
        $('#actual_datapoints_'+dataStreamId).text(data.data.length);
    }
    result.resolve(plot);//sent back for binding
}

function renderOverview(data, ranges)
{
    options = {
        legend: { show:false },
        series:     
        {
            lines: { show: true, lineWidth: 1 },
            shadowSize: 0   
        },
        grid: { color: "#999" },
        xaxis: 
        {     
            mode: "time", 
            timeformat: "%m-%d %h:%M %p",
            ticks: 5 ,
            min: ranges.xaxis.from,
            max: ranges.xaxis.to
        },
        selection: { mode: "x" }
    };

    if(data.min_value == null && data.max_value == null )
        options.yaxis = {min:data.min_value, max:data.max_value};
    else
        options.yaxis = {min:data.min_value, max:data.max_value,ticks:[data.min_value, data.max_value]};
    
    overviewPlots[data.datastream_id] = $.plot($("#overview"+data.datastream_id), [scale_data(data)], options);
}


/* Resets a graph back to it's original zoom level
 */
function resetZoom(streamId)
{
    if($("#zoom_sync_"+streamId).is(':checked'))         
    {
        divs = $(".portcullis-graph");
        for (var i = 0; i < divs.length; i++) 
        {
            var datastream_id = divs[i].id;
            if($("#zoom_sync_"+datastream_id).is(':checked'))         
            {
                overviewPlots[datastream_id].clearSelection(true);
                var overviewData = overviewPlots[datastream_id].getData();
                var ranges = {
                    xaxis: {
                        from: overviewData[0].xaxis.min,
                        to: overviewData[0].xaxis.max
                    }
                };
                delete overviewData[0]['lines'];
                delete overviewData[0]['shadowSize'];
                renderGraph(overviewData[0], ranges, false);
            }
        }
    }
    else {
        overviewPlots[streamId].clearSelection(true);
        var overviewData = overviewPlots[streamId].getData();
        var ranges = {
            xaxis: {
                from: overviewData[0].xaxis.min,
                to: overviewData[0].xaxis.max
            }
        };
        delete overviewData[0]['lines'];
        delete overviewData[0]['shadowSize'];
        renderGraph(overviewData[0], ranges, false);
    }
}

/*Responsible for keeping all graphs in sync (timewise) upon a date range
 *selection in flot. */
function zoom_all_graphs(ranges)
{
    divs = $(".portcullis-graph");
    for (var i = 0; i < divs.length; i++) 
    {
        var datastream_id = divs[i].id;
        if($("#zoom_sync_"+datastream_id).is(':checked'))         
            zoom_graph(ranges, datastream_id);
    }
}//end zoom_all_graphs

//update link to this specific view
function update_link()
{
    var start = new Date($("#start").val());
    var end = new Date($("#end").val());
    var streams = ''

    //TODO find all graphs on this page and create share link
    divs = $(".portcullis-graph");
    for (var i = 0; i < divs.length; i++) 
    {
        streams += '&view=' + divs[i].id
    }

    $("#share_link").attr("href","/graphs/?start="+ start.toLocaleString()+
                                           "&end="+end.toLocaleString()+
                                   "&granularity="+$("#granularity").val() + streams);
}//end update_link

function setupDownload(datastreamId)
{
        $('#downloadify'+datastreamId).downloadify({
        filename: function(){
            return 'datastream_'+datastreamId+'\.csv'; 
        },
        data: function(){ 
            return document.getElementById('sensor'+datastreamId+'_csv').value;
        },
        onComplete: function() { 
            //console.log("File with csv data for data stream "+datastreamId+" saved to disk."); //DEBUG 
        },
        onCancel: function() { 
            //console.log("File with csv data for data stream "+datastreamId+" cancelled."); //DEBUG 
        },
        onError: function() { 
            alert('You must put something in the File Contents or there will be nothing to save!'); 
        },
        transparent: false,
        swf: '/static/media/downloadify.swf',
        downloadImage: '/static/images/download.png',
        width: 100,
        height: 30,
        transparent: true,
        append: false
    });
}


