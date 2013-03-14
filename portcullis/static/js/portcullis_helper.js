/**
 * portcullis/static/js/portcullis_helpers.js
 *
 * Contributing Authors:
 *    Jeremiah Davis (jdavis@visgence.com)
 *
 * Copyright 2013, Visgence, Inc.
 *
 * This file contains some general helper functions for portcullis.
 */

/** Set up a spin indicator */
function spin(target, type) {
    var opts = null;
    if ( type == 'tiny' ) {
        opts = {
            lines: 9,
            length: 4,
            width: 1,
            radius: 3,
            corners: 0.5,
            rotate: 0,
            color: '#000000',
            speed: 1.5,
            trail: 54,
            shadow: false,
            hwaccel: false,
            className: 'spinIndicator',
            zIndex: 2e9,
            top: 'auto',
            left: '260px'
        };
    }
    else {
        opts = {
            lines: 20,
            length: 50,
            width: 4,
            radius: 30,
            corners: 0.5,
            rotate: 28,
            color: '#000000',
            speed: 1.5,
            trail: 54,
            shadow: false,
            hwaccel: false,
            className: 'spinIndicator',
            zIndex: 2e9,
            top: 'auto',
            left: 'auto'
        };
    }

    var spinIndicator = new Spinner(opts);
    spinIndicator.spin(target);
    return spinIndicator;
}

/** This method will create a dialogue and insert content from an ajax call
 *  into it.
 *
 * \param[in] view  The view to load into the dialog.
 * \param[in] title The title on the dialog.
 */
function makeDialog(view, title)
{
    $('body').append('<div id="serverDialog"></div>');
    var div = $('#serverDialog');
    $(div).addClass('serverDialog');

    // Find all the serverDialogs, and find the one with the largest id
    var IDs = $.map($('.serverDialog'), function(e, i) {
        return $(e).data('id');
    });

    console.log(IDs);

    var data_id = Math.max.apply(null,IDs) + 1;
    var id = 'serverDialog' + data_id;

    $(div).data('id', data_id);
    $(div).attr('id', id);
    $(div).css('display', 'none');
    $(div).attr('title', title);


    $('#' + id).dialog({
        autoOpen: true,
        resizable: true,
        hide: 'fade',
        show: 'fade',
        modal: false,
        minWidth: 300,
        maxWidth: 1000,
        minHeight: 300,
        maxHeight: 1000,
        dialogClass: "non-modal dialogue",
        close: function() {
            $(this).dialog('destroy');
            $('#' + id).remove();
        }
    });

    $.get(view, {}, function(resp) {
        console.log('Setting errors');
        if ( resp.errors ) {
            console.log(resp.errors);
        }
        console.log('Setting dialog html');
        $('#'+id).html(resp.html);
    });

}