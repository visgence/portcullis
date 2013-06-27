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

/** Readies the side panes tabs jquery ui */
function ready_tabs() 
{
    var tabs = $('#tabs').tabs({
        cache: true,
        beforeActivate: function(event, ui) {
            $('#widget_container').html('');
        }
    });
}

/** Checks the side panes anchor and determines if the user has scrolled it 
*   off the screen at the top.  If so make the side pane "sticky" and stay with the 
*   user down the page.
*/
function sidepane_relocate() 
{
    var window_top = $(window).scrollTop();
    var div_top = $('#side_pane_anchor').offset().top;

    var tab_strip = $('#tabs');
    var base_content = $('#base_content');

    //If the side pane height is greater than browser view.
    //Also, make sure we don't try this if there's note enough content height to scroll in
    if(tab_strip.height() > window.innerHeight && base_content.height() >= tab_strip.height()) {
        var doc_height = document.documentElement.clientHeight; 
        
        //Make sure we are either not scrolled to the bottom of document and that we are 
        //not scrolled to the top of the document.
        if(tab_strip.height() + tab_strip.offset().top < doc_height && 
           window_top <= tab_strip.offset().top &&
           window_top > div_top) {

            $('#side_pane').addClass('stick');
            $('#side_pane').removeClass('absolute');
            $('#side_pane').css('top', '');
        }
        //Must be scrolled at the bottom then.
        else if(window_top > div_top){

            var top_pos = $('#base_content').height() - tab_strip.height();
            $('#side_pane').removeClass('stick'); 
            $('#side_pane').addClass('absolute');
            $('#side_pane').css('top', top_pos);
        }
        //Else we're at the top of the page.
        else 
            $('#side_pane').removeClass('stick'); 
    }
    //Make sure we don't try this if there's note enough content height to scroll in
    else if(base_content.height() >= tab_strip.height()){
        if (window_top > div_top) {
            $('#side_pane').addClass('stick');
            $('#side_pane').removeClass('absolute');
            $('#side_pane').css('top', '');
        }
        else
            $('#side_pane').removeClass('stick'); 
    }
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
