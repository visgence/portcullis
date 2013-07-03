


/* Checks the url state and sets any default values that are missing */
$(function() {
    var state = $.bbq.getState();

    if(state.hasOwnProperty('tab') === false)
        state['tab'] = 'graphs';

    if(state['tab'] === "graphs") {
        if(state.hasOwnProperty('time') === false)
            state['time'] = 'hour';
        if(state.hasOwnProperty('auto-refresh') === false)
            state['auto-refresh'] = false;
    }
    $.bbq.pushState(state);
});


$(function() {

    var views = {

        'graphs': function(state) {
            console.log('view graphs fired');
            console.log(state);

            if(state.hasOwnProperty('time')) {
                $('#'+state['time']).prop('checked', true);

                if(state['time'] == "custom") {
                    if(state.hasOwnProperty('start'))
                        $('#start').val(state['start']);
                    if(state.hasOwnProperty('end'))
                        $('#end').val(state['end']);
                }

                $('#'+state['time']).trigger('change');
            }

            if(state.hasOwnProperty('auto-refresh') && state['auto-refresh'] == "true") {
                $('#auto_refresh').prop('checked', true);
                $('#auto_refresh').trigger('change');
            }
            else {
                $('#auto_refresh').prop('checked', false);
            }

            if(state.hasOwnProperty('streams')) {
                
                //Remove all graphs that do not have their id in the url
                $('#widget_container div.graph_container').each(function(i, container) {
                    var stream = $(container).prop('id').split('graph_container_')[1]
                    if($.inArray(stream, state['streams']) <= -1)
                        $(container).remove();
                });

                $('input.stream:checked').each(function(i, checkbox) {
                    var stream = $(checkbox).val();
                    if($.inArray(stream, state['streams']) <= -1)
                        $(checkbox).prop('checked', false);
                })
                
                //For each stream in url check it checkbox if possible and load it
                //if it has not been loaded already
                $.each(state['streams'], function(i, stream) {

                    var checkbox = $('input#stream_'+stream).get(0);
                    if(checkbox !== undefined) {
                        $(checkbox).prop('checked', true);

                        /*
                        //Remove found checkbox from list
                        var index = $.inArray(checkbox, checkboxes);
                        if(index > -1) {
                            checkboxes.splice(index, 1);
                        }*/
                    }

                    //If graph is already on the page
                    if($('#graph_container_'+stream).length > 0)
                        return;

                    var json = JSON.stringify({'stream': stream});
                    $.get('/graphs/', {'json_data': json}, function(data) {
                        $('#widget_container').append(data);
                        on_graph_load(stream, true);
                        $('#share_link').removeClass('display_none');
                    });

                });
            }
            else {
                $('input.stream:checked').prop('checked', false);
                $('#widget_container').empty();
            }
        }

        ,'utilities': function(state) {
            console.log('view utilities fired');
            console.log(state);
        }
    };

    /* Responds to any changes in the url hash for jquery bbq */
    $(window).bind('hashchange', function(event) {
        var state = event.getState();
        if(state.hasOwnProperty('tab') && views.hasOwnProperty(state['tab'])) {
            views[state['tab']](state);
        }
        else {
            //TODO: handle this with a 404 of some kind
            console.log('unrecognized view!');
        }
    });

});
