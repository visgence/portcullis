{% comment %}
/**
 * portcullis/static/js/crud.js
 *
 * Contributing Authors:
 *    Evan Salazar   (Visgence, Inc.)
 *    Jeremiah Davis (Visgence, Inc.)
 *    Bretton Murphy (Visgence, Inc.)
 *
 * Copyright 2013, Visgence, Inc.
 *
 * This file is a template for a dynamic javascript file to setup the 
 * KendoUI grid to manage models.  As long as this file takes to load, I think after development
 * is finished, it should be statically generated.
 */
{% endcomment %}


var grid;
var columns = {{columns|safe}};

var options = {
    enableCellNavigation: true,
    forceFitColumns: true,
    enableColumnReorder: true,
    fullWidthRows: true,
    showTopPanel: true,
};

var add_button = "<input type='button' value='Add' onclick='add_row();'/>";

$(function() {
    var data = {{data|safe}};
    grid = new Slick.Grid("#{{model_name}}_grid", data, columns, options);
    $(add_button).appendTo(grid.getTopPanel()); 
});

function add_row () 
{
    var columns = grid.getColumns();
    var new_row = {};

    for (var i = 0; i < columns.length; i++) {
        var col = columns[i];
        new_row[col.field] = '';
    }
    
    var rows = grid.getData();
    rows.splice(0, 0, new_row);
    grid.setData(rows);
    grid.render();
}
