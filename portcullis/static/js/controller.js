var state_cach = {};

/* Responds to any changes in the url hash for jquery bbq */
$(window).bind('hashchange', function(event) {
    var state = event.getState();
   
    if('tab' in state) {
        var newTab = $('.navbar-nav li[data-target="'+state['tab']+'"]');
        if(newTab.length <= 0)
            return;
        
        var current = $('.navbar-nav li.active');
        if(state['tab'] === $(current).data('target'))
            return;

        $('.'+$(current).data('target')).hide();
        $(current).removeClass('active');
        $(window).trigger(current+'-hidden');

        $('.navbar-nav li[data-target="'+state['tab']+'"]').addClass('active');
        $('.'+state['tab']).show();
        $(window).trigger(state['tab']+'-shown');
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
