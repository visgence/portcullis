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

function collapse_all(t_class) {
    /*
     * Grabs all specified section toggles and hides their sibling element
     *
     * t_class - The class of toggle div's that should be collapsed. Default is section_toggle which is all 
     *           div's that toggle.
     */

    if(t_class == "")
        t_class = "section_toggle";

    var element = $('.'+t_class);
    $(element).next().hide();
    
    var toggle_symbol = $(element).children('.collapse_state');
    if(toggle_symbol.html() == "-")
        toggle_symbol.html('+');
}

function collapse(t_id) {
    /*
     * Collapses one specific toggle section specified by by 
     *
     * t_id - The id of the div to toggle.
     */

    var element = $('#'+t_id);
    $(element).next().hide();

    var toggle_symbol = $(element).children('.collapse_state');
    if(toggle_symbol.html() == "-")
        toggle_symbol.html('+');
}


function check_all(check_id) {
    /*
     * Get's a checkbox and checks all of it's neighboring checkboxes if the checkbox was checked.
     * Neighboring checkboxes are ones that exist inside the same ul tag or div tag if no ul tag exists.
     *
     * check_id - Id of checkbox element.
     */

    var checkbox = $('#'+check_id+':checked');
    var parent_el = $(checkbox).parents('ul:first');

    //Just in case the checkboxes are not inside a ul
    if(!parent_el.length)
        parent_el = $(checkbox).parents('div:first');

    var checkboxes = $(parent_el).find('input[type="checkbox"]');
    checkboxes.each(function() {
        $(this).attr('checked', 'checked');
        $(this).trigger('change');
    });
}

function reset_check_all(checkbox, checkall_id) {
    /*
     * Checks if a checkbox was unchecked and if so unchecks it's corresponding checkall checkbox.
     *
     * checkbox    - The checkbox that has just changed state.
     * checkall_id - Id of checkall checkbox to uncheck.
     */

    if(!$(checkbox).attr('checked'))
        $('#'+checkall_id).removeAttr('checked');
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
