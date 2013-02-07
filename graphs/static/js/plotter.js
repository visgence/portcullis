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

function on_graphs_load() {
    /*
     * Sets up all graph bindings and loads all on screen graphs including a shared view if a auth token
     * is available within the template.
     */

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
    
    if (  $('#auth_token').val() )
        load_all_shared_graphs();
    else 
        load_all_graphs();
}


function on_graph_load(datastream_id) {
    /*
     * Sets up a specific graphs bindings and loads it's data.
     *
     * datastream_id - The stream whose data is to be loaded.
     */
    
    //bind main graph
    $("#sensor" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));
    $("#sensor" + datastream_id).bind("plotclick",create_plot_click_handler(datastream_id));
         
    //bind overview graph 
    $("#overview" + datastream_id).bind("plotselected",create_plot_select_handler(datastream_id));

    // setup the download link.
    setupDownload(datastream_id);
   
    load_graph(datastream_id, get_ranges(), graph_overview_callback());
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

function get_ranges() {
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
        end = new Date(start.getTime() + range*1000);
        $("#end").val(dateToString(end));
    }
    else if((end_range != "None" && start_range == "None" && !$("#start").val()) ||
            (!$("#start").val() && $("#end").val()))
    {
        start = new Date(end.getTime() - range*1000);
        $("#start").val(dateToString(start));
    }
    else if(!$("#start").val() && !$("#end").val())
    {    
        start = new Date(d.getTime() - range*1000);
        end= new Date(d.getTime());
 
        $("#start").val(dateToString(start));
        $("#end").val(dateToString(end));
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

    $('#'+data.datastream_id).removeClass('empty');

    return plot;
}


function zoom_graph(ranges, datastream_id) {
    /*
     * Gets a new data set for the specified time range and renders just the graph while leaving the overview alone.
     *
     * ranges        - Dict like object that contains the start and end range for the data set.
     * datastream_id - Id of the datastream to get new data for.
     */

    var options = { 
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

    //request data for the new timeframe
    load_graph(datastream_id, ranges, zoom_graph_callback(ranges));
}


function load_all_shared_graphs() {
    /*
     * Loads all data for graphs that belong to a shared view in the window.
     */

    var token = $('#auth_token').val();
    $('.portcullis-graph').each(function(i) {
        var url = '/graphs/sharedGraph/' + token + '/' + $('#saved_graph_'+this.id).val() + '/';
        $.get(url, graph_overview_callback());
    });
}

function load_all_graphs() {
    /*
     * Get's all graph divs and loads their data.
     */

    divs = $(".portcullis-graph");

    //Cycle though all graphs and fetch data from server
    for (var i = 0; i < divs.length; i++) 
    {
        load_graph(divs[i].id, get_ranges(), graph_overview_callback());
    }
}


function zoom_graph_callback(ranges) {
    /*
     * Returns a callback that renders a graph using data recieved from server after a user zooms the graph.
     * If there is no data then an empty graph is rendered with an appropriate message.
     *
     * ranges - Dict like object that contains the start and end range for the data set.
     *
     * Returns: Function that will be used as the callback function and takes the data recieved from server.
     */

    return function(data) {

        if(data.data.length == 0) {
            var msg = "No data for this range.";
            plot_empty_graph(data.datastream_id, msg);
        }
        else {
            renderGraph(data, ranges, true);
        }
        
        //Highlight zoomed section on overview graph
        overviewPlots[data.datastream_id].setSelection({xaxis: {from: ranges.xaxis.from, to: ranges.xaxis.to}}, true);

        //If user had datapoint selected then un-select it.
        reset_graph_selection(data.datastream_id);
    };
}

function graph_overview_callback() {
    /*
     * Returns a callback that renders a graph and overview using data recieved from server.  If there is no data
     * or insufficient privilages then an empty graph is rendered with an appropriate message.
     *
     * Returns: Function that will be used as the callback function and takes the data recieved from server.
     */

    var ranges = get_ranges();

    return function (data) {
        if(data.data.length == 0) {
            var msg = "No data for this range.";
            plot_empty_graph(data.datastream_id, msg);
            graph_options_visibility(data.datastream_id, 'none');
           
            //Add empty class so everything that needs graphs with data can ignore.
            $('#'+data.datastream_id).addClass('empty');
        }
        else if(!data.permission) {
            var msg = "You do not have permission to view this graph.";
            plot_empty_graph(data.datastream_id, msg);
            graph_options_visibility(data.datastream_id, 'none');
            
            //Add empty class so everything that needs graphs with data can ignore.
            $('#'+data.datastream_id).addClass('empty');
        }
        else {
            graph_options_visibility(data.datastream_id, '');

            //Make a full copy of the data since the two graphs need their own copy to work.
            var dData = $.extend(true, {}, data);
            renderGraph(data, ranges, true);
            renderOverview(dData, ranges);
            ready_minicolors(data.datastream_id);
        }

        //set the graphs title
        $("#graph_title" + data.datastream_id).text(data.ds_label);
    };
}

function load_graph(datastream_id, ranges, callback) {
    var granularity = get_granularity();

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
            min: !data['xmin'] ? ranges.xaxis.from : data['xmin']*1000 - timezone_offset,
            max: !data['xmax'] ? ranges.xaxis.to : data['xmax']*1000 - timezone_offset,
            ticks: 5
        },
        selection: {mode: "x"},
        grid: {
            clickable: true
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
            min: !data['xmin'] ? ranges.xaxis.from : data['xmin']*1000 - timezone_offset,
            max: !data['xmax'] ? ranges.xaxis.to : data['xmax']*1000 - timezone_offset
        },
        selection: { mode: "x" }
    };

    var default_color = $('#minicolor_'+data.datastream_id).val();
    if(default_color != '')
        data.color = default_color

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
        divs = $(".portcullis-graph:not(.empty)");
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
    divs = $(".portcullis-graph:not(.empty)");
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

    ranges = get_ranges();
    view['start'] = Math.round(ranges.xaxis.from/1000 + timezone_offset/1000);
    view['end'] = Math.round(ranges.xaxis.to/1000 + timezone_offset/1000);
    view['granularity'] = get_granularity();

    csrf = $('input[name="csrfmiddlewaretoken"]').val()

    $.post('/portcullis/createSavedView/', {'jsonData': JSON.stringify(view), 'csrfmiddlewaretoken': csrf},
           function (data) {
               $('#savedViewLink').html(data['html']);
           });
}

function ready_checkboxes() {
    /*
     * Get's any existing graphs on page and checks their respective checkbox.
     */

    //If any pre-loaded graphs are on page then check their stream checkbox
     var loaded_graphs = $('.portcullis-graph');
     loaded_graphs.each(function() { $('#stream_'+$(this).attr('id')).attr('checked', 'checked'); });
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

/**
 * This function is called when the submit button in the Streams control is pushed.
 * It gets the id's of the requested streams and makes an ajax request to render them
 * in the content pane.
 */
function get_selected_streams()
{
    var checked_streams = $.makeArray($('.stream:checked').map(function(index, element) {
        return $(this).val();
    }));

    if(checked_streams.length == 0)
        return;

    var get_data = new Object();

    get_data['streams'] = checked_streams;
    var json_data = JSON.stringify(get_data);

    $.get('/graphs/', {'json_data': json_data}, function(data){
        $('#content').html(data);
    });
}

function load_unload_stream(checkbox) {
    /*
     * Loads a stream to the page if it's checkbox was checked and unloads or stops the loading 
     * of the stream if it's checkbox is unchecked.
     *
     * checkbox - The streams checkbox input.
     */

    var datastream_id = $(checkbox).val();     
    if($(checkbox).attr('checked')) {
        var stream = new Object();
        stream['stream'] = datastream_id;
        var json = JSON.stringify(stream);

        //If we're already loading this graph
        if($('#graph_container_'+datastream_id).length)
            return;
        
        // append to widget container
        $.get('/graphs/', {'json_data': json}, function(data) {
            $('#widget_container').append(data);
            on_graph_load(datastream_id);
        });
    }
    else {
        var widget_container = $('#widget_container');
        $(widget_container).children('#graph_container_'+datastream_id).remove();
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
