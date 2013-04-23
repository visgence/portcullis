/**
*
* plotter.js
*
* script: This script has two primary functions. First, to retrieve all correctly formatted
* portcullis-graph divs from a page. Secondly, to query for data for the datastream ids.
*
**/
{% load url from future %}
// Returns plot select event handler  for binding

//global
var timezone_date = new Date();
var timezone_offset = timezone_date.getTimezoneOffset()*60*1000;//milliseconds
var overviewPlots = {};
var plots = {};

function create_plot_select_handler(datastream_id) 
{ 
    return function(event,ranges) 
    { 
        ranges.xaxis.from = new Date(ranges.xaxis.from + timezone_offset);
        ranges.xaxis.to = new Date(ranges.xaxis.to + timezone_offset);
        zoom_all_graphs(ranges);
    };
}//end create_plot_select_handler

function create_plot_click_handler(datastream_id, latestPos) 
{
    return function(event, pos, item) {
        var plot = plots[datastream_id];
        var axes = plot.getAxes();
        if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
            pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) {
            return;
        }

        var i, j, dataset = plot.getData();
        for (i = 0; i < dataset.length; ++i) {
            var series = dataset[i];
            // Find the nearest points, x-wise
            for (j = 0; j < series.data.length; ++j) {
                if(series.data[j] === null)
                    continue;
                if (series.data[j][0] > pos.x)
                    break;
            }

            // Now Interpolate
            var y;
            var p1 = series.data[j - 1];
            var p2 = series.data[j];
            if ((p1 !== null && p1 !== undefined) && (p2 !== null && p2 !== undefined) ) {
                y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]);
                var time = new Date(pos.x + timezone_offset);
                $('#graph_selection_'+datastream_id).removeAttr('style');
                $('#selected_value_'+datastream_id).text(y.toFixed(2));
                $('#selected_time_'+datastream_id).text(dateToString(time));
            }
            else
                reset_graph_selection(datastream_id);
        } 
    };
}

function set_graph_range_labels(start, end, datastream_id)
{
    $('#start_range_'+datastream_id).text(dateToString(start));
    $('#end_range_'+datastream_id).text(dateToString(end));
}

function reset_graph_selection(datastream_id)
{
    $('#graph_selection_'+datastream_id).attr('style', 'visibility: hidden;');
    $('#selected_value_'+datastream_id).text("");
    $('#selected_time_'+datastream_id).text("");
}


/** Hides a select graphs data container.
 *
 * Keyword Args
 *     datastream_id - The graph whose data container is to be hidden
 */
function hide_data_container(datastream_id)
{
    $("#stream_data_container_"+datastream_id).attr('style', 'display: none;');
}

/** Reveals a select graphs data container.
 *
 * Keyword Args
 *     datastream_id - The graph whose data container is to be revealed
 */
function show_data_container(datastream_id) 
{
    $("#stream_data_container_"+datastream_id).removeAttr('style'); 
}

/*
* Sets up all graph bindings and loads all on screen graphs including a shared view if a auth token
* is available within the template.
*/
function on_graphs_load() 
{

    //Find all portcullis graph divs
    $(".portcullis-graph").each(function(i) {

        var datastream_id = this.id;
        
        //bind main graphs
        $("#sensor" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));
        $("#sensor" + datastream_id).bind("plothover",create_plot_click_handler(datastream_id));
        $("#sensor" + datastream_id).bind("mouseleave", function(){ reset_graph_selection(datastream_id); });
         
        //bind  overview graph 
        $("#overview" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));

        // setup the download link.
        setupDownload(this.id);
    });
    
    if (  $('#auth_token').val() )
        load_all_shared_graphs();
    else 
        load_all_graphs();
}

//TODO: delete perm parameter when we get embeded graphs for sniffer working better
/*
 * Sets up a specific graphs bindings and loads it's data.
 *
 * datastream_id - The stream whose data is to be loaded.
 */
function on_graph_load(datastream_id, perm) 
{
    
    //bind main graph
    $("#sensor" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));
    $("#sensor" + datastream_id).bind("plothover",create_plot_click_handler(datastream_id));
    $("#sensor" + datastream_id).bind("mouseleave", function(){ reset_graph_selection(datastream_id); });
         
    //bind overview graph 
    $("#overview" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));

    // setup the download link.
    setupDownload(datastream_id);
  
    var period = get_period();
    if(!period)
        return;
    load_graph(datastream_id, period, graph_overview_callback(false, perm));
}


/* Gets the granularity currently set on the page. If it doesn't yet exist then a default is set and returned.
 *
 * Returns - Integer that is the currently set granularity.
 */
function get_granularity() 
{
    //Try and make default width of first graph otherwise default to 300
    var first_graph = $('.graph_container:first .sensor_graph');
    var default_granularity = first_graph.width();
    if(!default_granularity)
        default_granularity = 300;
  
    if($('#granularity').val() === null || $('#granularity').val() === undefined || $("#granularity").val() === '') {
        $("#granularity").val(default_granularity);
    }
    return $("#granularity").val();
}


//Time periods used for the time controls in miliseconds
var periods = {
    "hour":     60*60*1000,
    "24_hours": 24*60*60*1000,
    "week":     7*24*60*60*1000,
    "year":     365*24*60*60*1000
};


/** Shows or hides the error for the custom time period range.
 *
 * If no msg is given (i.e msg results int false) then no msg
 * is set if showing the error. This means any previous error set
 * if any will be shown.
 *
 * Keyword Args
 *     hide - Boolean that determines if error should be shown or hidden.
 *     msg  - Optional string for setting error message to.
 */
function custom_period_error(hide, msg)
{
    "use strict";
    if(hide)
        $('#custom_period_error').css('visibility', 'hidden');
    else {
        $('#custom_period_error').css('visibility', '');
        if(msg)
            $('#custom_period_error').text(msg);
    }
}

/** Get the time period specified by the graph time controls.
 *
 *  If custom time is specified but no start and/or end time is given an error
 *  is given.
 *
 * Return: Object containing the start and end time Date objects.
 * {
 *    'xaxis': {
 *       'from': start_time,
 *       'to':   end_time
 *    }
 * }
 */
function get_period() 
{
    "use strict";

    var start = null;
    var end = null;

    if($('#custom').attr('checked')) {
        if( !$('#start').val() || !$('#end').val() ) {
            custom_period_error(false, 'Please give a start and end date');
            return null;
        }

        start = (new Date($('#start').val()));
        end = (new Date($('#end').val()));
    }
    else {
        end = new Date();
        start = new Date(end.getTime() - periods[$('.period:checked').attr('id')]);
    }

    //Package up the dates properly
    var period = { 'xaxis': { 
        'from': start, 
        'to':   end
    }};

    custom_period_error(true);
    return period;
}


/** Get's and returns the range data for a particular graph.
 *
 *  This get's the current start and end ranges for the graph.
 *
 * Keyword Args
 *     g_id - The id of the datastream.
 *
 * Return: Dict like object containing xaxis ranges for the graph.
 *         {
 *            xaxis: {
 *              from: beginning x range,
 *              to  : ending x range
 *            },
 *            yaxis: {
 *              from: beginning y range,
 *              to  : ending y range
 *            }
 *         }
 */
function get_graph_range (g_id) 
{
    "use strict";

    var graph = plots[g_id];
    var axes = graph.getAxes();
    var ranges = {
        xaxis: {
            'from': new Date(axes.xaxis.min + timezone_offset),
            'to'  : new Date(axes.xaxis.max + timezone_offset)
        },
        yaxis: {
            'from': axes.yaxis.min,
            'to'  : axes.yaxis.max
        }
    };
    
    return ranges;
}

// scale incoming data
function scale_data(data)
{

    var tmpData = [];

    var avg_t_diff = 0;
    var t_diff = null;
    var n_t_diff = 0;
    var last_t = 0;

    data.raw_data = data.data;
    
    for(var i=0;i<data.data.length;i++) 
    {
        if (i > 0 && tmpData[tmpData.length-1]) {
            t_diff = data.data[i][0] - last_t;
            n_t_diff++;
            avg_t_diff = ((n_t_diff-1)*avg_t_diff + t_diff)/n_t_diff;
            if ( avg_t_diff > 0 && t_diff > 3*avg_t_diff )            
                tmpData.push(null);
        }
        last_t = data.data[i][0];
        var tmp = [];
        tmp[0] = data.data[i][0]*1000 - timezone_offset;//converting seconds to milliseconds
        tmp[1] = scaling_functions[data.scaling_function](data.data[i][1]);

        tmpData.push(tmp);
        
    }
    data.data = tmpData;
    return data;
}

function graph_options_visibility(datastream_id, display_css) {
    /*
     * Get's a specific graphs advanced options and overview and changes it's visibility by setting 
     * it's display css property.
     *
     * datastream_id - The graphs id who's options and overview will change.
     * display_css   - String that will be set as the 'display' css property.
     */

    var advanced_options = $('#advanced_options_'+datastream_id);
    var advanced_hook = $(advanced_options).prev('.graph_toggle');
    $('#overview'+datastream_id).css('display', display_css);
    $(advanced_options).css('display', display_css);
    $(advanced_hook).css('display', display_css);
    $(advanced_options).hide();
}

function plot_empty_graph(datastream_id, msg) {
    /*
     * Plots and returns an empty graph with a message in the graphs center.  
     *
     * datastream_id - The id of the stream itself.
     * msg           - The message to appear in the graphs center.
     *
     * Returns: Empty flot graph.
     */
    
    //Div hook for empty graph
    var div = "#sensor"+datastream_id;

    var empty_plot = $.plot($(div), [[2,2]], {
        bars: { show: true, barWidth: 0.5, fill: 0.9 },
        xaxis: {ticks: [], autoscaleMargin: 0.02, min: 0, max: 10},
        yaxis: { min: 0, max: 10 }
    });

    //Put in message for why graph is empty
    $(div).append('<span class="empty_graph_msg">'+msg+'</span>'); 
    hide_data_container(datastream_id);
    return empty_plot;
}

function plot_graph(data, options, div) {
    /*
     * Plots and returns a flot graph using given data and options.
     *
     * data    - Object structure containing data from server to graph.
     * options - Dictionary like object specifying how the graph should be created.
     * div     - String that is the id for the div hook for the graph to drawn to.
     *
     * Returns: A newly created flot graph. Shiny!
     */

    var default_color = $('#minicolor_'+data.datastream_id).val();
    if(default_color !== '')
        data.color = default_color;

    var scaled_data = scale_data(data);
    var csv="time,raw reading,scaled value\n";
    for (var i=0, j=0; i < scaled_data.data.length; i++) {
        if ( data.data[i]) {
            csv += data.raw_data[j][0]+",";
            csv += data.raw_data[j][1]+",";
            csv += scaled_data.data[i][1]+"\n";
            j++;
        }
    }
      
    var plot = $.plot($(div), [scaled_data], options);
    $(div+"_csv").html(csv);
    $('#datapoints_'+data.datastream_id).text(data.num_readings);
    $('#actual_datapoints_'+data.datastream_id).text(scaled_data.data.length);

    $('#'+data.datastream_id).removeClass('empty');

    return plot;
}

/*
 * Gets a new data set for the specified time range and renders just the graph while leaving the overview alone.
 *
 * ranges        - Dict like object that contains the start and end range for the data set.
 * datastream_id - Id of the datastream to get new data for.
 */
function zoom_graph(ranges, datastream_id) 
{
    //request data for the new timeframe
    load_graph(datastream_id, ranges, zoom_graph_callback(ranges, true));
}


function load_all_shared_graphs() {
    /*
     * Loads all data for graphs that belong to a shared view in the window.
     */
    var token = $('#auth_token').val();
    $('.portcullis-graph').each(function(i) {
        var url = '{{DOMAIN}}/api/sharedGraph/' + token + '/' + $('#saved_graph_'+this.id).val() + '/';
        $.get(url, graph_overview_callback(true, true));
    });
}

function load_all_graphs() {
    /*
     * Get's all graph divs and loads their data.
     */
    divs = $(".portcullis-graph");
    var period = get_period();
    if(!period)
        return;

    //Cycle though all graphs and fetch data from server
    for (var i = 0; i < divs.length; i++) 
        load_graph(divs[i].id, period, graph_overview_callback(false, true));
}


function zoom_graph_callback(ranges, select) {
    /*
     * Returns a callback that renders a graph using data recieved from server after a user zooms the graph.
     * If there is no data then an empty graph is rendered with an appropriate message.
     *
     * ranges - Dict like object that contains the start and end range for the data set.
     *
     * Returns: Function that will be used as the callback function and takes the data recieved from server.
     */

    return function(data) {

        if(data.data.length === 0) {
            var msg = "No data for this range.";
            plots[data.datastream_id] = plot_empty_graph(data.datastream_id, msg);
            hide_data_container(data.datastream_id);
        }
        else {
            renderGraph(data, ranges, true);
            show_data_container(data.datastream_id);
        }
       
        if (select){
            //Highlight zoomed section on overview graph
            overviewPlots[data.datastream_id].setSelection({
                xaxis: {
                    from: ranges.xaxis.from.getTime() - timezone_offset, 
                    to:   ranges.xaxis.to.getTime() - timezone_offset
                }
            }, true);
        }
        //If user had datapoint selected then un-select it.
        reset_graph_selection(data.datastream_id);
    };
}

//TODO: delete perm permission when we get embeded graphs working better for sniffer
function graph_overview_callback(is_shared, perm) {
    /*
     * Returns a callback that renders a graph and overview using data recieved from server.  If there is no data
     * or insufficient privilages then an empty graph is rendered with an appropriate message.
     *
     * Returns: Function that will be used as the callback function and takes the data recieved from server.
     */

    var ranges = get_period();

    return function (data) {
        
        if (is_shared) {
            var start = data.xmin*1000;
            var end = data.xmax*1000;
            $('#custom').attr('checked', 'checked');
            $('.custom_period').removeAttr('disabled');
            $('#start').val(dateToString(new Date(start)));
            $('#end').val(dateToString(new Date(end)));
            $('#granularity').val(data.granularity);
        }

        var msg = '';
        if(data.data.length === 0) {
            msg = "No data for this range.";
            plots[data.datastream_id] = plot_empty_graph(data.datastream_id, msg);
            graph_options_visibility(data.datastream_id, 'none');
           
            //Add empty class so everything that needs graphs with data can ignore.
            $('#'+data.datastream_id).addClass('empty');
        }
        else if(!data.permission || !perm) {
            msg = "You do not have permission to view this graph.";
            plots[data.datastream_id] = plot_empty_graph(data.datastream_id, msg);
            graph_options_visibility(data.datastream_id, 'none');
            
            //Add empty class so everything that needs graphs with data can ignore.
            $('#'+data.datastream_id).addClass('empty');
        }
        else {
            graph_options_visibility(data.datastream_id, '');
            
            //Make a full copy of the data since the two graphs need their own copy to work.
            var dData = $.extend(true, {}, data);
            // Do not give the zoom info to the overview.
            dData.zoom_start = undefined;
            dData.zoom_end = undefined;
            renderGraph(data, ranges, true);
            renderOverview(dData, ranges);
            ready_minicolors(data.datastream_id);
        }

        //set the graphs title
        $("#graph_title" + data.datastream_id).text(data.ds_label);

        // For saved views, refresh the graph
        if ( data.zoom_start )
            refresh_graph(data.datastream_id);
    };
}

function load_graph(datastream_id, ranges, callback) {
    var granularity = get_granularity();
    
    var indicator_s = spin(document.getElementById('stream_span_' + datastream_id), 'tiny');
    var indicator_g = spin(document.getElementById('graph_container_' + datastream_id));

    var getData = {};
 
    getData.start = Math.round(ranges.xaxis.from.getTime()/1000);
    getData.end = Math.round(ranges.xaxis.to.getTime()/1000);
    getData.granularity =  granularity;
    getData.datastream_id = datastream_id;
    getData.reduction = $('#reduction_select_' + datastream_id).val();
    
    json_data = JSON.stringify(getData);
    $.get("{{DOMAIN}}{% url 'api-render_graph' %}", {'json_data': json_data}, function(data) {
        indicator_s.stop();
        indicator_g.stop();
        if(typeof(data) == 'string')
            data = JSON.parse(data);
        callback(data);
    });
}

function renderGraph(data, ranges, shouldScale)
{
    var result = $.Deferred();
    var dataStreamId = data.datastream_id;
    var xmin = null;
    var xmax = null;

    if (data.zoom_start)
        xmin = new Date(data.zoom_start * 1000);
    else if (data.xmin) {
        xmin = new Date(data.xmin * 1000);
    }
    else
        xmin = ranges.xaxis.from;

    if (data.zoom_end)
        xmax = new Date(data.zoom_end * 1000);
    else if ( data.xmax ) {
        xmax = new Date(data.xmax * 1000);
    }
    else
        xmax = ranges.xaxis.to;
  
    var options = 
    { 
        lines: { show: true }, 
        xaxis: 
        {     
            mode: "time", 
            timeformat: " %m-%d %h:%M %p",
            min: xmin.getTime() - timezone_offset,
            max: xmax.getTime() - timezone_offset,
            ticks: 5
        },
        selection: {mode: "x"},
        crosshair: {mode: "x"},
        grid: {
            hoverable: true,
            autoHighlight: false
        }
    };
    
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
    show_data_container(dataStreamId);
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
            min: !data.xmin ? ranges.xaxis.from : data.xmin*1000 - timezone_offset,
            max: !data.xmax ? ranges.xaxis.to : data.xmax*1000 - timezone_offset
        },
        selection: { mode: "x" }
    };

    var default_color = $('#minicolor_'+data.datastream_id).val();
    if(default_color !== '')
        data.color = default_color;

    if(data.min_value === null && data.max_value === null )
        options.yaxis = {min:data.min_value, max:data.max_value};
    else
        options.yaxis = {min:data.min_value, max:data.max_value,ticks:[data.min_value, data.max_value]};
    
    overviewPlots[data.datastream_id] = $.plot($("#overview"+data.datastream_id), [scale_data(data)], options);
}

/** Reloads a graph that has data while preserving they're zoom state. 
 *
 *  Keyword Arguments:
 *      g_id - The datastream id to refresh
 * */
function refresh_graph(g_id) 
{
    //Only refresh graphs that actually contain data
    if(g_id in plots) {
        var ranges = get_graph_range(g_id);
        load_graph(g_id, ranges, zoom_graph_callback(ranges, false));
    }
}

/** Reloads all graphs that have data while preserving they're zoom state. */
function refresh_graphs () 
{
    var divs = $('.portcullis-graph');
    $(divs).each(function (i, div) {
        var g_id = $(div).attr('id');
        refresh_graph(g_id);
    });
}

/** Resets a graph back to it's original zoom level
 */
function resetZoom(streamId)
{
    var overviewData = null;
    var ranges = null;
        
    divs = $(".portcullis-graph:not(.empty)");
    for (var i = 0; i < divs.length; i++) 
    {
        var datastream_id = divs[i].id;
        overviewPlots[datastream_id].clearSelection(true);
        overviewData = overviewPlots[datastream_id].getData();
        ranges = { xaxis: {
            from: new Date(overviewData[0].xaxis.min + timezone_offset),
            to:   new Date(overviewData[0].xaxis.max + timezone_offset)
        }};
        load_graph(datastream_id, ranges, zoom_graph_callback(ranges, false)); 
    }
    
    reset_graph_selection(streamId);
}

/** Given a time range (x-axis) reloads all graphs using that range.
 *
 *  ranges - Dict like object containing the new ranges.
 *           {
 *              xaxis: {
 *                 from: epoch seconds
 *                 to:   epoch seconds
 *              }
 *           }
 */
function zoom_all_graphs(ranges)
{
    divs = $(".portcullis-graph:not(.empty)");
    for (var i = 0; i < divs.length; i++) 
        zoom_graph(ranges, divs[i].id);
}

/** Initializes the download button under a given graphs Advanced Options.
 *  
 *  datastream_id - Id of stream who's download button is to be initialized.
 */
function setupDownload(datastream_id)
{
    $('#downloadify'+datastream_id).downloadify({
        filename: function(){
            return 'datastream_'+datastream_id+'.csv'; 
        },
        data: function(){ 
            return document.getElementById('sensor'+datastream_id+'_csv').value;
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
        append: false
    });
}


/** Enables or disables custom time period inputs based on the radio button given.
 *
 *  If the radio input has a value of 'custom' then the start and end date fields 
 *  become enabled while everything else results in them becoming disabled.
 *
 * Keyword Args
 *     radio - Radio input element that was clicked on.
 */
function toggle_time_periods(radio) 
{
    if($(radio).val() == "custom") {
        $('.custom_period').removeAttr('disabled');
        if($('#start').val() && $('#end').val())
            load_all_graphs();
    } 
    else {
        $('.custom_period').attr('disabled', 'disabled');
        custom_period_error(true);
        load_all_graphs();
    }
}


/** Save this view and give the link to it.
*   TODO: Expand to save all widgets, not just graphs, maybe in another js file?
*         Also, expand to include zoom info, and info per widget/graph instead of page wide
*/
function saveView()
{
    var view = {};
    view.graphs = $.makeArray($('.portcullis-graph').map(function(index, domElement) {
        var graph = {};
        graph.ds_id = this.id;
        try {
            var zrange = get_graph_range(this.id);
            graph.zoom_start = Math.round(zrange.xaxis.from/1000.0 + timezone_offset/1000.0);
            graph.zoom_end = Math.round(zrange.xaxis.to/1000.0 + timezone_offset/1000.0);
        } catch (e) {
            console.log('Error getting zoom ranges: ' + e);
            // graph has no data here, so it is not zoomed
            graph.zoom_start = null;
            graph.zoom_end = null;
        }
        
        graph.reduction = $('#reduction_select_'+this.id).val();
        return graph;
    }));

    ranges = get_period();
    view.start = Math.round(ranges.xaxis.from/1000 + timezone_offset/1000);
    view.end = Math.round(ranges.xaxis.to/1000 + timezone_offset/1000);
    view.granularity = get_granularity();

    csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.post('{{DOMAIN}}{% url "api-create-saved-view" %}', {'jsonData': JSON.stringify(view), 'csrfmiddlewaretoken': csrf},
           function (data) {
               if ( 'errors' in data ) {
                   span = '<span></span>';
                   $(span).css('color', 'red').html(data.errors);
                   $('#savedViewLink').html(data.errors);
               }
               else
                   $('#savedViewLink').html(data.html);
           });
}

/** Get's any existing graphs on page and checks their respective checkbox.
*/
function ready_checkboxes() 
{
    //If any pre-loaded graphs are on page then check their stream checkbox
     var loaded_graphs = $('.portcullis-graph');
     loaded_graphs.each(function() { $('#stream_'+$(this).attr('id')).attr('checked', 'checked'); });
}

/** Creates the minicolor pickers inside each graphs advanced options space.
*/
function ready_minicolors(datastream_id)
{ 
    var graph_data = plots[datastream_id].getData();
    var default_color = graph_data[0].color;

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
            graph_data[0].color = hex;
            overview_data[0].color = hex;

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


/** Finds the start and end date picker inputs and initializes them for use.
*/
function ready_datepickers()
{

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


function get_graph(ds_id, token)
{
    var json = JSON.stringify({'datastream_id': ds_id, 'token': token});
    
    // append to widget container
    $.get('{{DOMAIN}}{% url "graphs-simple_graph" %}', {'json_data': json}, function(data) {
        $('#graphs').append(data.graph);
        on_graph_load(ds_id ,data.perm);
    });
}

/** Loads a stream to the page if it's checkbox was checked and unloads or stops the loading 
 * of the stream if it's checkbox is unchecked.
 *
 * checkbox - The streams checkbox input.
 */
function load_unload_stream(checkbox) 
{
    var datastream_id = $(checkbox).val();     
    if($(checkbox).attr('checked')) {
        if(!get_period()) {
            $(checkbox).removeAttr('checked');
            return;
        }
        var stream = {};
        stream.stream = datastream_id;
        var json = JSON.stringify(stream);

        //If we're already loading this graph
        if($('#graph_container_'+datastream_id).length)
            return;
        
        // append to widget container
        $.get('{{DOMAIN}}{% url "graphs" %}', {'json_data': json}, function(data) {
            $('#widget_container').append(data);
            on_graph_load(datastream_id, true);
            $('#share_link').removeClass('display_none');
        });
    }
    else {
        var widget_container = $('#widget_container');
        $(widget_container).children('#graph_container_'+datastream_id).remove();
        
        if(!$('.graph_container').length)
            $('#share_link').addClass('display_none');
    }
}


/** Take a Date object and return a string formatted as:
 * mm/dd/yyyy HH:MM:SS
 */
function dateToString(date)
{
    dStr = String(date.getMonth() + 1) + '/' + String(date.getDate()) + '/' + String(date.getFullYear()) + 
        ' ' + String(date.getHours()) + ':' + String(date.getMinutes()) + ':' + String(date.getSeconds());
    return dStr;
}

/** Takes a UTC timestamp in seconds and converts it into a local timezone timestamp in miliseconds.
 *
 * Keyword Args
 *     timestamp - UTC timestamp in seconds
 *
 * Return: A timestamp converted from the UTC time to the local timezone time.
 */
function utc_to_local(timestamp) 
{
    //Create date obj for local timezone offset
    var tz_date = new Date();
    var tz_offset = tz_date.getTimezoneOffset()*60*1000;

    //Turn to miliseconds then add in time zone offset
    var local_timestamp = timestamp*1000 - tz_offset;

    return local_timestamp;
}


/** Checks that status of the auto_refresh checkbox to see if it's checked. If it is then
 *  a time interval of 30 seconds is set to refresh all graphs.
 *
 * Keyword Args
 *     chk_ele - Checkbox element that was clicked
 */
function auto_refresh(chk_ele)
{
    if($(chk_ele).attr('checked')) {
        var refreshBtn = $('#refresh');
        
        setInterval(function() {
            if($('#auto_refresh').attr('checked')) {
                console.log('refreshing!');
                $(refreshBtn).trigger('click');
            }
        }, 30000);
    }
}
