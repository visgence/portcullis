$(window).bind('hashchange', function(event) {
    console.log(event.getState());
    var state = event.getState();

    if('time' in state) {
        $('#'+state['time']).attr('checked', 'checked');

        if(state['time'] == "custom") {
            if('start' in state)
                $('#start').val(state['start']);
            if('end' in state)
                $('#end').val(state['end']);
        }

        $('#'+state['time']).trigger('change');
    }
});
