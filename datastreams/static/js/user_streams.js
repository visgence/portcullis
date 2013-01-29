function load_user_graphs()
{
    var checked_streams = $('.stream:checked');
    var owned_streams = [];
    var public_streams = [];
    var view_streams = [];

    for(var i = 0; i < checked_streams.length; i++) {
        var stream = $(checked_streams[i]);

        if(stream.attr('name') == "owned")
            owned_streams.push(stream.val());
        else if(stream.attr('name') == "view")
            view_streams.push(stream.val());
        else if(stream.attr('name') == "public")
            public_streams.push(stream.val());
    }

    var get_data = new Object();
    get_data['view'] = view_streams;
    get_data['public'] = public_streams;
    get_data['owned'] = owned_streams;

    var json_data = JSON.stringify(get_data);

    $.get('/graphs/', {'json_data': json_data}, function(data){
        var previous_controls = $('#graph_controls');
        if(previous_controls.length > 0)
           previous_controls.remove();

        $('#side_pane_content').prepend(data.controls);
        $('#content').html(data.graphs);
    });
}
