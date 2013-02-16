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

/* Extra html for grids  */
var add_button = "<input type='button' value='Add' onclick='dataModel.add_row();'/>";
var delete_button = "<input type='button' value='Delete'/>";


/* Grid configurations */

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
        },
        set_data: function(new_data) {
            this.data = new_data;
        },
        prepend_data: function(new_row) {
            this.data.splice(0, 0, new_row); 
        }
    },
    model_name: '',

    columns: null,

    options: {
        editable: true,
        enableCellNavigation: true,
        forceFitColumns: true,
        enableColumnReorder: true,
        fullWidthRows: true,
        showTopPanel: true
    },

    grid: null,

    refresh: function() {
        self = this;
        Dajaxice.portcullis.read_source(
            function(response) {
                self.model.data = response;
                self.grid.invalidate();
            },
            {model_name: self.model_name}
        );
    },

    add_row: function() {
        var grid = this.grid;
        var model = this.model;

        var columns = grid.getColumns();
        var new_row = {};

        for (var i = 0; i < columns.length; i++) {
            var col = columns[i];
            new_row[col.field] = '';
        }
       
        model.prepend_data(new_row);
        grid.invalidate();
    },

    error: function(msg) {
        console.log('Error: msg');
    }
};

$(function() {
    dataModel.model_name = $('#model_name').val();
    Dajaxice.portcullis.get_columns(
        function(resp) {
            dataModel.columns = resp;
            dataModel.grid = new Slick.Grid("#" + dataModel.model_name + "_grid", dataModel.model, dataModel.columns, dataModel.options);
            $(add_button).appendTo(dataModel.grid.getTopPanel()); 
            $(delete_button).appendTo(dataModel.grid.getTopPanel()); 
            dataModel.grid.setSelectionModel(new Slick.RowSelectionModel());
            dataModel.refresh();
        },
        {'model_name': dataModel.model_name}
    );
});
