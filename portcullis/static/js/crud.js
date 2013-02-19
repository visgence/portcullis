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
var add_button = '<input type="button" value="Add" onclick="myGrid.add_row();"/>';
var delete_button = '<input type="button" value="Delete" onclick="myGrid.delete_row();"/>';
var save_button = '<input type="button" value="Save" onclick="myGrid.save_all_rows();"/>';
var refresh_button = '<input type="button" value="Refresh" onclick="myGrid.refresh();"/>';
var myGrid = null;


/* Grid configuration */
function DataGrid() {
    /** This is the object that contains the data.  It allows for more
     *  dynamic data in the grid.
     */
    this.model = {
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
        setItem: function(index, item) {
            this.data[index] = item;
        },
        set_data: function(new_data) {
            this.data = new_data;
        },
        prepend_data: function(new_row) {
            this.data.splice(0, 0, new_row); 
        },
        remove_data: function(index) {
            this.data.splice(index,1);
        }
    };

    /** This is the name of the django model to we are creating the grid for. */
    this.model_name = '';

    /** The column definition for the grid.  This is loaded via ajax. */
    this.columns = null;

    /** These are the slickGrid options.*/
    this.options = {
        editable: true,
        enableCellNavigation: true,
        forceFitColumns: true,
        enableColumnReorder: true,
        fullWidthRows: true,
        showTopPanel: true
    };

    this.grid = null;

    /** Method to get data from server and refresh the grid.*/
    this.refresh = function() {
        self = this;
        Dajaxice.portcullis.read_source(
            function(resp) {
                var data = resp;

                // Make sure on refresh to mark everything gotten from the server as unedited.
                for (var i = 0; i < data.length; i++)
                    data[i]['_isNotEdited'] = true;
                
                self.model.set_data(data);
                self.grid.invalidate();
            },
            {model_name: self.model_name}
        );
    };

    /** Method to add a row */
    this.add_row = function() {
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
    };

    /** Method to save all the modified rows, checks the _isNotEdited flag */
    this.save_all_rows = function() {
        self = this;
        // Go through the models, and if a row has been edited, save it.
        for (var i = 0; i < this.model.getLength(); i++) {
            console.log(i);
            console.log(this.model.getItem(i));
            if (!this.model.getItem(i)._isNotEdited) {
                var callback = function(index) {
                    var i = index;
                    return function(resp) {
                        if ('errors' in resp) {
                            self.error(resp['errors'])
                            return;
                        }
                        else {
                            console.log(resp);
                            console.log(i);
                            self.model.setItem(i, resp[0]);
                            self.model.getItem(i)._isNotEdited = true;
                            //self.grid.invalidateRow(i);
                            //self.grid.render();
                            //self.grid.invalidate();
                            self.success('Updated row ' + i);
                        }
                    };
                };
                Dajaxice.portcullis.update(callback(i),
                                           {'model_name': this.model_name, 'data': this.model.getItem(i)});
            }
        }
    }; // End save_all_rows

    /** Method to remove a row from the grid */
    this.remove_row = function(index) {
        this.model.remove_data(index);
        this.grid.invalidate();
    };

    /** Method to delete the selected row. */
    this.delete_row = function() {
        // get the selected row, right now assume only one.
        var selected = this.grid.getSelectedRows();
        if (selected.length != 1) {
            this.error("Error, we don't have exactly 1 data item selected!");
            return;
        }
        var row = this.grid.getData()[selected[0]];
        // If there is an id, send an ajax request to delete from server, otherwise, just
        // remove it from the grid.
        if (this.model.getItem(selected)['_isNotEdited'] === true) {
            self = this;
            Dajaxice.portcullis.destroy(
                function(resp) {
                    if ('errors' in resp) {
                        self.error(resp['errors']);
                        return;
                    }
                    else if ('success' in resp) {
                        self.remove_row(selected);
                        self.success(resp.success);
                    }
                    else
                        self.error('Unknown error has occurred on delete.');
                },
                {'model_name': this.model_name, 'data': this.model.getItem(selected)}
            );
        }
        else {
            this.remove_row(selected);
            this.success('Locally removed row: ' + selected + '.');
        }
    };
        
    /** Stuff to do on error. */
    this.error = function(msg) {
        console.log('Error: ' + msg);
    };

    /** Stuff to do on success. */
    this.success = function(msg) {
        console.log('Success: ' + msg);
    };

    /** Here we initialize our object. */
    this.init = function() {
        this.model_name = $('#model_name').val();
        self = this;
        Dajaxice.portcullis.get_columns(
            function(resp) { 
                self.columns = resp;

                // Add editors to columns
                for ( var i = 0; i < self.columns.length; i++) { //var col in self.columns.length ) {
                    if (self.columns[i]._editable == true) {
                        switch (self.columns[i]._type) {
                        case 'boolean':
                            self.columns[i].editor = Slick.Editors.Checkbox;
                            self.columns[i].formatter = Slick.Formatters.Checkmark;
                            break;
                        case 'integer':
                            self.columns[i].editor = Slick.Editors.Integer;
                            break;
                        case 'date':
                            self.columns[i].editor = Slick.Editors.Date;
                            break;
                        case 'text':
                            self.columns[i].editor = Slick.Editors.LongText;
                            break;
                        case 'foreignkey':
                            self.columns[i].formatter = foreign_key_formatter;
                            break;
                        case 'number':
                        case 'char':
                        default:
                            self.columns[i].editor = Slick.Editors.Text;
                        }
                    }
                }
                
                self.grid = new Slick.Grid("#" + self.model_name + "_grid", self.model, self.columns, self.options);

                // Add controls
                $(add_button).appendTo(self.grid.getTopPanel()); 
                $(delete_button).appendTo(self.grid.getTopPanel());
                $(save_button).appendTo(self.grid.getTopPanel());
                $(refresh_button).appendTo(self.grid.getTopPanel());
                
                self.grid.setSelectionModel(new Slick.RowSelectionModel());

                // Add some listeners
                self.grid.onCellChange.subscribe(function (e, args) {
                    args.item._isNotEdited = false;
                });

                self.refresh();
            },
            {'model_name': self.model_name}
        );
    };

    this.init();
}

function foreign_key_formatter (row, cell, columnDef, dataContext) {
    console.log(dataContext);
    console.log(row);
    return "test";
}

$(function() {
    myGrid = new DataGrid();
    
});
