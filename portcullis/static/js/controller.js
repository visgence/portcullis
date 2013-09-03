

/* Responds to any changes in the url hash for jquery bbq */
$(window).bind('hashchange', function(event) {
    console.log('hashchanged');
    var state = event.getState();
    if('tab' in state) {
        var newTab = $('.navbar-nav li[data-target="'+state['tab']+'"]');
        if(newTab.length <= 0)
            return;

        $('#widget_container').html('');
        var current = $('.navbar-nav li.active');
        $('#'+$(current).data('target')).hide();
        $(current).removeClass('active');

        $('.navbar-nav li[data-target="'+state['tab']+'"]').addClass('active');
        $('#'+state['tab']).show();
    }

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
