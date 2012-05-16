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


function create_plot_select_handler(datastream_id) 
{ 
    return function(event,ranges) 
    { 
        //ranges.xaxis.from = ranges.xaxis.from - timezone_offset;
        //ranges.xaxis.to = ranges.xaxis.to - timezone_offset;
        zoom_all_graphs(ranges);
        var start = new Date(ranges.xaxis.from + timezone_offset);
        var end= new Date(ranges.xaxis.to + timezone_offset);

        //$("#start").val(start.toString());
        $("#start").datetimepicker('setDate', start);
        $("#end").datetimepicker('setDate', end);
//        $("#end").val(end.toString());
        update_link();
    } 
}//end create_plot_select_handler

//On load function will search for any 'portcullis-graph' divs on the page.
$("document").ready(function ()
{
    var d = new Date();
    //print out utc date/time    
    $("#utc_stamp").html(d.toUTCString());//DEBUG
    
    var range = (48 * 60 * 60);    
    //var timezone_offset = (d.getTimezoneOffset()/60) * 60 *60 * 1000;
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
        $("#granularity").val(100);//default
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
    zoom_all_graphs(ranges);
    update_all_overviews(ranges);
    update_link();
});//end on_load

// scale incoming data
function scale_data(data)
{
    for(var i=0;i<data.data.length;i++) 
    {
        data.data[i][0] = data.data[i][0]*1000 - timezone_offset;//converting seconds to milliseconds
        //data.data[i][0] = data.data[i][0]*1000;
        data.data[i][1] = scaling_functions[data.scaling_function](data.data[i][1]) 
    }
    return data;
}

/*Plots a  graph.
* returns: plot object
*/
function plot_graph(data,options,div)
{
 
    //If no data then say so inside empty graph
    if(data.data.length==0)
    {  
        var empty_plot = $.plot($(div), [[2,2]], 
                        {
                            bars: { show: true, barWidth: 0.5, fill: 0.9 },
                            label:  data.name, 
                            xaxis: {ticks: [], autoscaleMargin: 0.02, min: 0, max: 10 },
                            yaxis: { min: 0, max: 10 }
                        });
        //inform the user that there is no data for this sensor 
        var offset = empty_plot.pointOffset({ x: 4, y: 5});
        $(div).append('<div style="position:absolute;width:800px;text-align:center;top:' + offset.top + 'px;color:#666;font-size:smaller">No Data for '+ data.name + ' in this range</div>');
    }//end if
    else
    {
        var plot = $.plot($(div), [scale_data(data)], options);
        return plot;
    }
}//end plot_graph

//queries for a time range(datepicker)
function submit_form(datastream_id)
{   
    var start = new Date($("#start").val());
    var end = new Date($("#end").val());
    
    epoch_start = start.getTime();
    epoch_end= end.getTime();  
    
    epoch_start -= timezone_offset;
    epoch_end -= timezone_offset;

    var ranges = { xaxis: { from: epoch_start , to: epoch_end }};
    zoom_all_graphs(ranges);
    update_all_overviews(ranges);
    update_link();
}//end submit_form

/*queries for data for a single datastream and a specific time period
 * ranges: date range for the query
 * granularity: how many data points the result should aim for
*/
function zoom_graph(ranges, granularity, datastream_id)
{

    var result = $.Deferred();
    //alert(ranges.xaxis.from); //Generate the options for flot
    var options = 
    { 
        lines: { show: true }, 
        xaxis: 
        {     
            mode: "time", 
            timeformat: " %d-%m %h:%M::%S %p",
            min: ranges.xaxis.from,
            max: ranges.xaxis.to,
            ticks: 5
        },
        selection: {mode: "x"}
    };
  
    //$("#debug").html(ranges.xaxis.from + " to " + ranges.xaxis.to);//DEBUG

    //plot the data that we receive
    function on_data_recieved(data) 
    {
        //set the graphs title
        $("#graph_title" + datastream_id).text(data.name + " - Node " + data.node_id + " - Stream " + datastream_id );

        options.yaxis = {min:data.min_value, max:data.max_value, axisLabel: data.units};
        var plot =  plot_graph(data,options,"#sensor" + datastream_id);
        result.resolve(plot);//sent back for binding
    }//end on data_recieved

    //request data for the new timeframe
    $.ajax(    
    {
        url:"/render_graph/?json=true&start=" + Math.round(ranges.xaxis.from/1000 + timezone_offset/1000 )  + "&end=" + Math.round(ranges.xaxis.to/1000 + timezone_offset/1000) + "&granularity=" + granularity + "&datastream_id=" + datastream_id,
        method: 'GET',
        dataType: 'json',
        success: on_data_recieved
    });

    return result;
}//end zoom_graph

function update_overview(ranges, datastream_id)
{
    function setup_overview(data) 
    {
        options =
        {
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
                timeformat: "%d-%m %h:%M %p",
                ticks: 5 ,
                min: ranges.xaxis.from,
                max: ranges.xaxis.to

            },
            selection: { mode: "x" }
        };

        if(data.min_value == null && data.max_value == null )
        {
            options.yaxis = {min:data.min_value, max:data.max_value};
        }
        else
        {
            options.yaxis = {min:data.min_value, max:data.max_value,ticks:[data.min_value, data.max_value]};
        }

        $.plot($("#overview" + datastream_id),[scale_data(data)],options);
    }//end setup_overview

    //send request for overview
    $.ajax(    
    {
        url:"/render_graph/?json=true&start=" + Math.round(ranges.xaxis.from/1000 + timezone_offset/1000) + "&end=" + Math.round(ranges.xaxis.to/1000 + timezone_offset/1000) + "&granularity=" + $("#granularity").val() + "&datastream_id=" + datastream_id,
        method: 'GET',
        dataType: 'json',
        success: setup_overview
    });

}//end update_overview


/*Responsible for keeping all graphs in sync (timewise) upon a date range
 *selection in flot. */
function zoom_all_graphs(ranges)
{
    divs = $(".portcullis-graph");

    for (var i = 0; i < divs.length; i++) 
    {
        var datastream_id = divs[i].id;
        zoom_graph(ranges, $("#granularity").val(), datastream_id);
    }
}//end zoom_all_graphs

function update_all_overviews(ranges)
{
    divs = $(".portcullis-graph");

    for (var i = 0; i < divs.length; i++) 
    {
        var datastream_id = divs[i].id;
        update_overview(ranges,datastream_id);
    }
}//end update_all_overviews

//update link to this specific view
function update_link()
{
    var start = new Date($("#start").val());
    var end = new Date($("#end").val());
    var node = getURLParameter("node");

    if(node != 'null')
    {
        $("a").attr("href","/?node="+node +"&start="+ start.toLocaleString()+"&end="+end.toLocaleString());
    }
    else
    {
        $("a").attr("href","/?start="+ start.toLocaleString()+"&end="+end.toLocaleString());
    }
}//end update_link

function getURLParameter(name)
{
    return decodeURI
    (
        (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]
    );
}//end getURLParameter
