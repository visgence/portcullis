
function toggle_form_section(event) {
    /*
     * This function toggles the corresponding sibling div of the header
     * that calls it
     */
    
    var element = $(event.target);
    element.next().toggle('slow');
}

function collapse_all() {
    $('.section_toggle').next().hide();
}
