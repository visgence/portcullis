function toggle_form_section(event) {
    /*
     * This function toggles the corresponding sibling div of the header
     * that calls it
     */
   
    var toggle_options = {
        'duration': 0,
        'easing': 'linear'
    };

    var element = $(event.target);
    if($(element).hasClass('collapse_state'))
        element = $(element).parent();
    else if($(element).is('b'))
        element = $(element).parent();

    element.next().toggle(toggle_options);

    var toggle_symbol = $(element).children('.collapse_state');
    if(toggle_symbol.html() == '+')
        toggle_symbol.html('-');
    else if(toggle_symbol.html() == "-")
        toggle_symbol.html('+');
}

function collapse_all() {
    /*
     * Grabs all section toggles and hides their sibling element
     */

    $('.section_toggle').next().hide();
}

function sidepane_relocate() {
    /*
     * Checks the side panes anchor and determines if the user has scrolled it 
     * off the screen at the top.  If so make the side pane "sticky" and stay with the 
     * user down the page.
     */
    
    var window_top = $(window).scrollTop();
    var div_top = $('#side_pane_anchor').offset().top;

    if (window_top > div_top)
        $('#side_pane').addClass('stick')
    else
        $('#side_pane').removeClass('stick'); 
}
