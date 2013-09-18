
$(function() {
    var default_tab = 'graphs';

    var tabs = {
        'graphs': function(state) {
            if('time' in state) {
                $('#'+state['time']).prop('checked', true);

                if(state['time'] == "custom") {
                    if('start' in state)
                        $('#start').val(state['start']);
                    if('end' in state)
                        $('#end').val(state['end']);
                }

                $('#'+state['time']).trigger('change');
            }

            if('auto-refresh' in state && state['auto-refresh'] == "true") {
                $('#auto_refresh').prop('checked', true);
                $('#auto_refresh').trigger('change');
            }
            else {
                $('#auto_refresh').removeAttr('checked');
            }
        }
        ,'sensors': function() {}
        ,'utilities': function() {}
    };

    /* Responds to any changes in the url hash for jquery bbq */
    $(window).bind('hashchange', function(event) {
        var state = event.getState();
    
        if('tab' in state) {
            if($.fn.Nav.isTab(state['tab']) === false)
                return;
           
            var current = $.fn.Nav.getActive();
            if(state['tab'] === current) {
                tabs[state['tab']](state)
                return;
            }
            console.log('loading tab');
            if($.fn.Nav.isLoaded(state['tab']))
                $.fn.Nav.activate(state['tab'], false);
            else
                $.fn.Nav.activate(state['tab'], true);

            $(window).one(state['tab']+'-loaded', function() {tabs[state['tab']](state)});
        }
        else if($.fn.Nav.isActive(default_tab) === false) {
            $.fn.Nav.activate(default_tab, true);
            $(window).one(default_tab+'-loaded', function() {tabs[default_tab](state)});
        }

    });

    $(window).trigger('hashchange');
});
