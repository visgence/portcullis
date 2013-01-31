/**
*
* plotter.js
*
* script: This script has two primary functions. First, to retrieve all correctly formatted
* portcullis-graph divs from a page. Secondly, to query for data for the datastream ids.
*
**/

// Returns plot select event handler  for binding

//global
var timezone_date = new Date();
var timezone_offset = timezone_date.getTimezoneOffset()*60*1000//milliseconds
var overviewPlots = {};
var plots = {};

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
    } 
}//end create_plot_select_handler

function create_plot_click_handler(datastream_id) 
{
    return function (event, pos, item) {
        if (item) {
            var value = item['datapoint'][1];
            var epoch = item['datapoint'][0];
            var time = new Date(epoch + timezone_offset);

            $('#graph_selection_'+datastream_id).removeAttr('style');
            $('#selected_value_'+datastream_id).text(value);
            $('#selected_time_'+datastream_id).text(time.toLocaleString());
        }
        else
            reset_graph_selection(datastream_id);
    };
}

function set_graph_range_labels(start, end, datastream_id)
{
    var start_date = new Date(start + timezone_offset);
    var end_date = new Date(end  + timezone_offset);

    $('#start_range_'+datastream_id).text(start_date.toLocaleString());
    $('#end_range_'+datastream_id).text(end_date.toLocaleString());
}

function reset_graph_selection(datastream_id)
{
    $('#graph_selection_'+datastream_id).attr('style', 'display: none;');
    $('#selected_value_'+datastream_id).text("");
    $('#selected_time_'+datastream_id).text("");
}

/// This method should be called when graphs are loaded.
function on_graphs_load()
{
    if(!$("#granularity").val()) 
        get_granularity()
 
    //Find all portcullis graph divs
    $(".portcullis-graph").each(function(i) {

        var datastream_id = this.id;
        
        //bind main graphs
        $("#sensor" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));
        $("#sensor" + datastream_id).bind("plotclick",create_plot_click_handler(datastream_id));
         
        //bind  overview graph 
        $("#overview" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));

        // setup the download link.
        setupDownload(this.id);
    });
    
    ready_datepickers();
}


function modify_date(date, date_range, subtract) {
    /* Takes a Date object and adds/subtracts a range of time from it based on the date_range passed in.
     *
     * date       - Date object to modify.
     * date_range - The range to to modify the date by. "One Day", "One Week", "One Month".
     * subtract   - Boolean to tell if we're subtracting the range from the date or not.
     *
     * Returns    - New Date object modified according to the parameters
     */

    var edit_amount = 1;
    var new_date = new Date(date.toLocaleString());

    if(date_range == "One Week")
        edit_amount = 7;
    
    if(subtract)
        edit_amount = -edit_amount;

    if(date_range == "One Month")
        new_date.setMonth(new_date.getMonth() + edit_amount);
    else
        new_date.setDate(new_date.getDate() + edit_amount);

    return new_date;
}

function get_granularity() {
    /* Gets the granularity currently set on the page. If it doesn't yet exist then a default is set and returned.
     *
     * Returns - Integer that is the currently set granularity.
     */

    //Try and make default width of first graph otherwise default to 300
    var first_graph = $('.graph_container:first .sensor_graph');
    var default_granularity = first_graph.width();
    if(!default_granularity)
        default_granularity = 300;

    if($("#granularity").val() == '')
        $("#granularity").val(default_granularity) 

    return $("#granularity").val();
}

function getRanges() {
    var d = new Date();
    var range = (48 * 60 * 60);    
    var epoch_start;
    var epoch_end;
    var start = new Date($("#start").val());
    var end = new Date($("#end").val());
    
    var start_range = $('#start_range').val();
    var end_range = $('#end_range').val();  
    
    if((start_range != "None" && end_range == "None" && !$("#end").val()) ||
       ($("#start").val() && !$("#end").val()))
    {
        end = new Date(d.getTime());
        $("#end").val(end.toLocaleString());
    }
    else if((end_range != "None" && start_range == "None" && !$("#start").val()) ||
            (!$("#start").val() && $("#end").val()))
    {
        start = new Date(d.getTime() - range*1000);
        $("#start").val(start.toLocaleString());
    }
    else if(!$("#start").val() && !$("#end").val())
    {    
        start = new Date(d.getTime() - range*1000);
        end= new Date(d.getTime());
 
        $("#start").val(start.toLocaleString());
        $("#end").val(end.toLocaleString());
    }

    if(start_range != "None")
        start = modify_date(end, start_range, true);
    else if(end_range != "None")
        end = modify_date(start, end_range, false);

    epoch_start = start.getTime() - timezone_offset;
    epoch_end = end.getTime() - timezone_offset;
    
    var range_data = { 
        xaxis: { 
                  from: epoch_start, 
                    to: epoch_end,
        }
    };
    return range_data;
}

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
        var default_color = $('#minicolor_'+data.datastream_id).val();
        if(default_color != '')
            data.color = default_color

        var scaled_data = scale_data(data);
        var csv="time,raw reading,scaled value\n";
        for (var i in scaled_data['data']) {   
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
function submit_form()
{   
    get_granularity();
    loadAllGraphs(getRanges());
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
        selection: {mode: "x"},
        grid: {
            clickable: true
        }
    };

    //plot the data that we receive
    function on_data_recieved(data) 
    {
        //set the graphs title
        $("#graph_title" + datastream_id).text(data.ds_label + " - Node " + data.node_id + " - Stream " + datastream_id );

        //Highlight zoomed section on overview graph
        overviewPlots[datastream_id].setSelection({xaxis: {from: ranges.xaxis.from, to: ranges.xaxis.to}}, true);

        options.yaxis = {min:data.min_value, max:data.max_value, axisLabel: data.units};
        var plot =  plot_graph(data,options,"#sensor" + datastream_id);
        result.resolve(plot);//sent back for binding

        set_graph_range_labels(ranges.xaxis.from, ranges.xaxis.to, datastream_id);
        reset_graph_selection(datastream_id);
    }//end on data_recieved

    //request data for the new timeframe
    loadGraph(datastream_id, get_granularity(), ranges, on_data_recieved);

    return result;
}//end zoom_graph


function loadAllSharedGraphs(ranges)
{
    var granularity = get_granularity();
    var token = $('#auth_token').val();
    $('.portcullis-graph').each(function(i) {
        var url = '/graphs/sharedGraph/' + token + '/' + $('#saved_graph_'+this.id).val() + '/';
        $.get(url, graph_overview_callback(ranges));
    });
}

function loadAllGraphs(ranges)
{
    divs = $(".portcullis-graph");
    var granularity = get_granularity()

    //Cycle though all graphs and fetch data from server
    for (var i = 0; i < divs.length; i++) 
    {
        loadGraph(divs[i].id, granularity, ranges, graph_overview_callback(ranges));
    }
}

function graph_overview_callback(ranges) {
    return function (data) {
                
        //Make a full copy of the data since the two graphs need their own copy to work.
        var dData = $.extend(true, {}, data);
        renderGraph(data, ranges, true);
        renderOverview(dData, ranges);
        ready_minicolors(data.datastream_id);
    }
}

function loadGraph(datastream_id, granularity, ranges, callback) {
    var getData = new Object();
    getData['start'] = Math.round(ranges.xaxis.from/1000 + timezone_offset/1000);
    getData['end'] = Math.round(ranges.xaxis.to/1000 + timezone_offset/1000);
    getData['granularity'] =  granularity;
    getData['datastream_id'] = datastream_id;
    getData['reduction'] = $('#reduction_select_' + datastream_id).val();

    json_data = JSON.stringify(getData);
    $.get("/graphs/render_graph/", {'json_data': json_data}, callback);
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
        selection: {mode: "x"},
        grid: {
            clickable: true
        }
    };
    
    //set the graphs title
    $("#graph_title" + dataStreamId).text(data.ds_label);
    options.yaxis = {min:data.min_value, max:data.max_value, axisLabel: data.units};
    var plot;
    if(shouldScale)
        plot = plot_graph(data,options,"#sensor" + dataStreamId);
    else
    {
        plot = $.plot($("#sensor" + dataStreamId), [data], options);
        $('#datapoints_'+dataStreamId).text(data.num_readings);
        $('#actual_datapoints_'+dataStreamId).text(data.data.length);
    }
    result.resolve(plot);//sent back for binding
    plots[dataStreamId] = plot;
    set_graph_range_labels(ranges.xaxis.from, ranges.xaxis.to, dataStreamId);
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
    
    reset_graph_selection(streamId);
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
            alert('You must have actual data points or there is nothing to save!'); 
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

function toggle_date_range(select, date_id, mutable_select)
{
    var date_field = $("#"+date_id);
    var selected = $(select).val();
    
    if(selected != "None")
    {
        date_field.attr('disabled', 'disabled');
        $('#'+mutable_select).attr('disabled', 'disabled');
    }
    else
    {
        date_field.removeAttr('disabled');
        $('#'+mutable_select).removeAttr('disabled');
    }
}


/// Save this view and give the link to it.
/// TODO: Expand to save all widgets, not just graphs, maybe in another js file?
///       Also, expand to include zoom info, and info per widget/graph instead of page wide
function saveView()
{
    var view = new Object();
    view['graphs'] = $.makeArray($('.portcullis-graph').map(function(index, domElement) {
        var graph = new Object();
        graph['ds_id'] = this.id;
        graph['reduction'] = $('#reduction_select_'+this.id).val();
        return graph;
    }));

    ranges = getRanges();
    view['start'] = Math.round(ranges.xaxis.from/1000 + timezone_offset/1000);
    view['end'] = Math.round(ranges.xaxis.to/1000 + timezone_offset/1000);
    view['granularity'] = get_granularity();

    csrf = $('input[name="csrfmiddlewaretoken"]').val()

    console.log(view['graphs']);
    console.log(JSON.stringify(view['graphs'][0]));
    //    stuff = JSON.stringify(view);

    $.post('/portcullis/createSavedView/', {'jsonData': JSON.stringify(view), 'csrfmiddlewaretoken': csrf},
           function (data) {
               console.log(data);
               $('#savedViewLink').html(data['html']);
           });
}

function ready_minicolors(datastream_id)
{ 
    /*
     * Creates the minicolor pickers inside each graphs advanced options space.
     */

    var graph_data = plots[datastream_id].getData();
    var default_color = graph_data[0]['color'];

    $('#minicolor_'+datastream_id).minicolors({
        animationSpeed: 100,
        animationEasing: 'swing',
        change: null,
        control: 'wheel',
        defaultValue: default_color,
        hide: function() {
            var hex = this.minicolors('value');
            var graph = plots[datastream_id];
            var overview = overviewPlots[datastream_id];
           
            //Get the current data set to change color
            var graph_data = graph.getData();
            var overview_data = overview.getData();
             
            //Change color within data
            graph_data[0]['color'] = hex;
            overview_data[0]['color'] = hex;

            //Set the data back and tell graphs to draw
            plots[datastream_id].setData(graph_data);
            overviewPlots[datastream_id].setData(overview_data);

            plots[datastream_id].draw();
            overviewPlots[datastream_id].draw();

        },
        hideSpeed: 100,
        inline: false,
        letterCase: 'lowercase',
        opacity: false,
        position: 'top',
        show: null, 
        showSpeed: 100,
        swatchPosition: 'left',
        textfield: true,
        theme: 'none'     
    });
}

function ready_datepickers()
{
    /*
     * Finds the start and end date picker inputs and initializes them for use.
     */

    $('#start').datetimepicker
    ({
        showSecond: true,
        dateFormat: 'mm/dd/yy',
        timeFormat: 'hh:mm:ss',
        onSelect: function (selectedDateTime)
        {
            var start = $(this).datetimepicker('getDate');
            $('#end').datetimepicker('option', 'minDate', new Date(start.getTime()));
        }
    });
    $('#end').datetimepicker
    ({
        showSecond: true,
        dateFormat: 'mm/dd/yy',
        timeFormat: 'hh:mm:ss',
        onSelect: function (selectedDateTime)
        {
            var end = $(this).datetimepicker('getDate');
            $('#start').datetimepicker('option', 'maxDate', new Date(end.getTime()));
        }
    });

}

