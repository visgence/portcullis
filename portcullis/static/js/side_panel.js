/*
 * portcullis/static/side_panel.js
 * Contributing Authors:
 *    Jeremiah Davis (Visgence, Inc.)
 *    Bretton Murphy (Visgence, Inc.)
 *
 * (c) 2013 Visgence, Inc.
 *
 * This file contains functions for side_panel (navigation) functionality.
 */

/** Toggle hide the side panel. */
function toggle_side_pane() 
{
    // Make sure to toggle the arrow direction.
    if ( $('#side_pane_button .ui-icon-circle-triangle-w').length ) {
        $('#side_pane_button').button('option', 'icons', {primary: 'ui-icon-circle-triangle-s'});
        $('#content').css('margin-left', '300px');
        $('#side_pane').css('width', '300px');
    }
    else if ( $('#side_pane_button .ui-icon-circle-triangle-s').length ) {
        $('#side_pane_button').button('option', 'icons', {primary: 'ui-icon-circle-triangle-w'});
        $('#content').css('margin-left', '20px');
        $('#side_pane').css('width', '20px');
    }
    $('#side_pane_content').toggle('slide', {direction: 'left'}, 'fast');
}

var tabContent = {};

/** Readies the side panes tabs jquery ui */
function ready_tabs() 
{
    var tabs = $('#tabs').tabs({
        beforeActivate: function(event, ui) {
            $('#widget_container').html('');
        },
        activate: function(event, ui) {
            $.bbq.pushState({'tab': ui.newTab.text().toLowerCase()});
        }
    });
}


/** Gets the html for managing a users streams and puts it in the content of the page */
function load_model_grid(app, model) 
{
    var url = "/utilities/model_editor/"+app+"/"+model+"/";
    $.get(url, {}, function(data) {
        $('#widget_container').html(data);  
    });
}

/** Get the html for the next level of the stream sub_tree. */
function toggle_subtree(event)
{
    var toggle_options = {
        'duration': 0,
        'easing': 'linear'
    };
    
    var element = $(event.target);
    if($(element).hasClass('collapse_state'))
        element = $(element).parent();
    else if($(element).is('b'))
        element = $(element).parent();

    div = element.next();

    var toggle_symbol = $(element).children('.collapse_state');
    if(toggle_symbol.html() == '+'){
        if (div.text() == '') {
            Dajaxice.portcullis.stream_subtree(function(resp) {
                if ( 'errors' in resp ) {
                    console.log('Error getting subtree: ' + resp.errors);
                    return false;
                }
                $(div).html(resp.html);
                $(div).find('input.stream').each(function(i, input) {
                    if($.inArray($(input).val(), checkedGraphs) > -1)
                        $(input).prop('checked', true);
                });

                div.toggle(toggle_options);
                toggle_symbol.html('-');
            }, {'name': $(element).attr('id'), group: $(element).attr('group')});
        }
        else {
            div.toggle(toggle_options);
            toggle_symbol.html('-');
        }
    }
    else if(toggle_symbol.html() == "-") {
        div.toggle(toggle_options);
        toggle_symbol.html('+');
    }
}
