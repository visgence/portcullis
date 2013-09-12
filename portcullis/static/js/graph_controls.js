/*
 * graphs/static/graph_controls.js
 * Contributing Authors:
 *    Jeremiah Davis (Visgence, Inc.)
 *    Bretton Murphy (Visgence, Inc.)
 *
 * (c) 2013 Visgence, Inc.
 */

/** Readies the side panes tabs jquery ui */
function ready_tabs() 
{
    $.get('/graphs/streams/', function(resp) {
        $('div.side-nav div#stream-tree').html(resp);
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

            $.get('/graphs/streams/get_subtree/', {
                  'jsonData': JSON.stringify({'name': $(element).attr('id'), group: $(element).attr('group')})
            }, function(resp) {
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
            });
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
