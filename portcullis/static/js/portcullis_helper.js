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
    if ( type == 'tiny' ) {
        var opts = {
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
        var opts = {
            lines: 25,
            length: 100,
            width: 5,
            radius: 40,
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