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

var columns = {{columns|safe}};

var options = {
    enableCellNavigation: true,
    forceFitColumns: true,
    enableColumnReorder: true,
    fullWidthRows: true,
    showTopPanel: true
};

var add_button = "<input type='button' value='Add' onclick='add_row();'/>";

var dataModel = {
    model: {
        data: [],
        getItem: function(i) {
            return this.data[i];
        },
        getItemMetaData: function(i) {
            return null;
        },
        getLength: function() {
            return this.data.length;
        }
    },
    
    grid: null,

    refresh: function() {
        self = this;
        Dajaxice.portcullis.read_source(
            function(response) {
                self.model.data = response;
                self.grid.invalidate();
            },
            {model_name: '{{model_name}}'}
        );
    }
};

$(function() {
    dataModel.grid = new Slick.Grid("#{{model_name}}_grid", dataModel.model, columns, options);
    $(add_button).appendTo(dataModel.grid.getTopPanel()); 
    dataModel.refresh();
});

function add_row () 
{
    var grid = dataModel.grid;
    var columns = grid.getColumns();
    var new_row = {};

    for (var i = 0; i < columns.length; i++) {
        var col = columns[i];
        new_row[col.field] = '';
    }
    
    var rows = grid.getData().data;
    rows.splice(0, 0, new_row);
    grid.setData(rows);
    grid.render();
}
