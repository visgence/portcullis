
$(function() {
    var default_tab = 'graphs';

    /* Responds to any changes in the url hash for jquery bbq */
    $(window).bind('hashchange', function(event) {
        var state = event.getState();
    
        if('tab' in state) {
            if($.fn.Nav.isTab(state['tab']) === false)
                return;
           
            var current = $.fn.Nav.getActive();
            if(state['tab'] === current)
                return;

            if($.fn.Nav.isLoaded(state['tab'])) {
                $.fn.Nav.activate(state['tab'], false);                
            }
            else 
                $.fn.Nav.activate(state['tab'], true);
        }
        else if($.fn.Nav.isActive(default_tab) === false) {
            $.fn.Nav.activate(default_tab, true);
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

    $(window).trigger('hashchange');
});
