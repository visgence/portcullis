/*
 * portcullis/static/side_panel.js
 * Contributing Authors:
 *    Jeremiah Davis (Visgence, Inc.)
 *
 * (c) 2013 Visgence, Inc.
 *
 * This file contains functions for side_panel (navigation) functionality.
 */

/** Toggle hide the side panel. */
function toggle_side_pane() {
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