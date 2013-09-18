$(function() {
    var stateCache = {};
    var currentRequest = null;
    var tabUris = {
        'graphs': '/graphs/index'
        ,'utilities': '/portcullis/utilities/index/'
        ,'sensors': '/portcullis/sensors/index/'
    };
    var properStates = {
        'graphs':['time', 'auto-refresh', 'start', 'end']
        ,'utilities': []
        ,'sensors': []
    };

    $('ul.navbar-nav').on('click', 'li', function(e) {
        var newTab = $(e.currentTarget).data('target');
        if(isActive(newTab) === false)
            activate(newTab, true);
    });

    var changeHashTab = function(newTab) {
        var newState = {
            'tab': newTab
        };

        $.bbq.pushState(newState, 2);
    };

    var isTab = function(tab) {
        tab = tab || '';
        return $('ul.navbar-nav li[data-target="'+tab+'"]').length > 0 ? true:false;
    };

    var isActive = function(tab) {
        tab = tab || '';
        return $('ul.navbar-nav li[data-target="'+tab+'"]').hasClass('active');
    };

    var getActive = function() {
        return $('ul.navbar-nav li.active').data('target');
    };

    var activate = function(tab, loadContent) {
        tab = tab || '';
        var toActivate = $('ul.navbar-nav li[data-target="'+tab+'"]');
        if(toActivate.length > 0) {
            $('ul.navbar-nav li[class="active"]').removeClass('active');
            $(toActivate).addClass('active');
            changeHashTab(tab);
            if(loadContent === true)
                loadActive();
        }
    };

    var isLoaded = function(tab) {
        tab = tab || '';
        return $('#'+tab+'-container').length > 0 ? true:false;
    };

    var loadActive = function() {
        var active = getActive();
        if(tabUris.hasOwnProperty(active)) {
            $.get(tabUris[active], function(resp) {
                $('#base-content').html(resp);
                $(window).trigger(active+'-loaded');
            });
        }
    };

    $.fn.Nav = {
        'isActive': isActive
        ,'activate': activate
        ,'getActive': getActive
        ,'isTab': isTab
        ,'isLoaded': isLoaded
    };
});
