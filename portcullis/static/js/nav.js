$(function() {
    var stateCache = {};
    var currentRequest = null;
    var tabUris = {
        'graphs': '/graphs/index'
        ,'utilities': '/portcullis/utilities/index/'
    };
    var properStates = {
        'graphs':['time', 'auto-refresh', 'start', 'end'], 
        'utilities': []
    };

    $('ul.navbar-nav').on('click', 'li', function(e) {
        var newTab = $(e.currentTarget).data('target');
        if(isActive(newTab) === false)
            activate(newTab);
    });

    var changeHashTab = function(newTab) {

        var state = $.bbq.getState();
        
        if(state.hasOwnProperty('tab')) {
            currentTab = state['tab'];

            var stateToSave = {};
            $.each(state, function(key, val) {
                if($.inArray(key, properStates[currentTab]) > -1)
                    stateToSave[key] = val;
            });
            stateCache[currentTab] = stateToSave;
        }

        var newState = {
            'tab': newTab
        };
        if(stateCache.hasOwnProperty(newTab) && stateCache[newTab] !== undefined)
            $.extend(true, newState, stateCache[newTab]);
        console.log(newState);
        $.bbq.pushState(newState, 2);
    };

    var isTab = function(tab) {
        tab = tab || '';
        console.log($('ul.navbar-nav li[data-target="'+tab+'"]').length > 0 ? true:false);
        return $('ul.navbar-nav li[data-target="'+tab+'"]').length > 0 ? true:false;
    };

    var isActive = function(tab) {
        tab = tab || '';
        return $('ul.navbar-nav li[data-target="'+tab+'"]').hasClass('active');
    };

    var getActive = function() {
        return $('ul.navbar-nav li.active').data('target');
    };

    var activate = function(tab) {
        tab = tab || '';
        var toActivate = $('ul.navbar-nav li[data-target="'+tab+'"]');
        if(toActivate.length > 0) {
            $('ul.navbar-nav li[class="active"]').removeClass('active');
            $(toActivate).addClass('active');
            changeHashTab(tab);
            loadActive();
        }
    };

    var loadActive = function() {
        var active = getActive();
        if(tabUris.hasOwnProperty(active)) {
            $.get(tabUris[active], function(resp) {
                $('#base-content').html(resp);
            });
        }
    };

    $.fn.Nav = {
        'isActive': isActive
        ,'activate': activate
        ,'getActive': getActive
        ,'isTab': isTab
    };
});
