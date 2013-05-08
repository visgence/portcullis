

/* Responds to any changes in the url hash for jquery bbq */
$(window).bind('hashchange', function(event) {
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

    if('auto-refresh' in state && state['auto-refresh'] == "true") {
        $('#auto_refresh').attr('checked', 'checked');
        $('#auto_refresh').trigger('change');
    }
    else {
        $('#auto_refresh').removeAttr('checked');
    }
});
