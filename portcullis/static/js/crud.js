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


(function($) {
    /* Extra html for grids  */
    var add_button = '<input type="button" value="Add" onclick="myGrid.add_record();"/>';
    var delete_button = '<input type="button" value="Delete" onclick="myGrid.delete_row();"/>';
    var edit_button = '<input type="button" value="Edit" onclick="myGrid.edit_record();"/>';
    var refresh_button = '<input type="button" value="Refresh" onclick="myGrid.refresh();"/>';
    var message_span = '<span id="server_messages" style="padding-left:1em"></span>';

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
            get_pk: function(i) {
                return this.data[i]['pk'];
            },
            get_cell_data: function(i, j) {
                return this.data[i][j];
            },
            setItem: function(i, item) {
                this.data[i] = item;
            },
            set_data: function(new_data) {
                this.data = new_data;
            },
            prepend_data: function(new_row) {
                this.data.splice(0, 0, new_row); 
            },
            remove_data: function(i) {
                this.data.splice(i, 1);
            }
        };

        /** This is the name of the django model to we are creating the grid for. */
        this.model_name = '';

        /** The column definition for the grid.  This is loaded via ajax. */
        this.columns = null;

        /** These are the slickGrid options.*/
        this.options = {
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
            this.clear_row_selection();
            Dajaxice.portcullis.read_source(
                function(resp) {
                    if ( 'errors' in resp ) {
                        self.error(mesg);
                        return;
                    }
                    else
                        $('#server_messages').html('');
                    
                    // Make sure on refresh to mark everything gotten from the server as unedited.
                    for (var i = 0; i < resp.length; i++)
                        resp[i]['modified'] = false;
                    
                    self.model.set_data(resp);
                    self.grid.invalidate();
                },{
                    model_name: self.model_name
                });
        };

        /** Method to add a record */
        this.add_record = function() {
            //Clear row selection
            this.clear_row_selection();

            var add_form = get_grid_form(this.columns);
            if (add_form) {
                $('#'+this.model_name+'_grid').append(add_form.div);
                confirm_dialog(add_form.id, 'Add', add_record_callback, 'Cancel', null, true);
            }
            else
                console.log('no editable columns');
        };

        /** Method to edit a selected record in the grid. */
        this.edit_record = function() {
            var selected_index = this.grid.getSelectedRows();
            var selected_row = this.model.getItem(selected_index);
            var edit_form = get_grid_form(this.columns, selected_row);

            if (edit_form) {
                var edit_callback = function() {edit_record_callback(selected_index);};
                $('#'+this.model_name+'_grid').append(edit_form.div);
                confirm_dialog(edit_form.id, 'Save', edit_callback, 'Cancel', null, true);
            }
            else
                console.log('edit form didnt exist.');
        };

        /** Method to add new row to beginning of grid
         *
         * Keyword Args
         *    new_row - Dictionary containing new row data.
         */
        this.add_row = function(new_row) {
            self = this;
            
            self.save_row(0, new_row, false);
        };

        /** Method to add edited row at a given index
         *
         * Keyword Args
         *    edited_row - Dict containing the new edited row data.
         *    index      - Index of the row that was edited.
         */
        this.add_edited_row = function(edited_row, index) {
            self = this;
            
            edited_row['pk'] = self.model.get_pk(index);
            self.save_row(index, edited_row, true);
        };

        /** Callback method for save_row when a server response has been recieved.
         *
         * Keyword Args
         *    i      - Index of row that was being edited
         *    update - Boolean for if we're updating a row or creating one.
         *
         * Return: Function that handles the response object from server.
         */
        this.save_callback = function(i, update) {
            self = this;

            return function(resp) {
                //Reset server message
                $('#server_messages').html('');

                if ('errors' in resp) {
                    self.error(resp['errors']);
                    return;
                }
                else {
                    //Either add new row to beginning or update one.
                    if (update) {
                        self.model.setItem(i, resp[0]);
                        self.grid.invalidateRow(i);
                    }
                    else {
                        self.model.prepend_data(resp[0]);
                        self.grid.invalidateAllRows();
                    }
                    
                    self.grid.render();
                    self.success('Updated row ' + i);
                }
                self.clear_row_selection();
            };
        };

        /** Saves a specified row if it is modified.
         *
         * Keyword Args
         *    i      - Index of row to be saved.
         *    row    - Dictinary containing the row data save.
         *    update - Boolean for if this is an update or a new row.
         */
        this.save_row = function(i, row, update) {
            
            Dajaxice.portcullis.update(this.save_callback(i, update), {
                'model_name': this.model_name, 
                'data': row
            });
        };
 
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
            if (this.model.getItem(selected)['modified'] === false) {
                self = this;
                var delete_func = function() {
                    Dajaxice.portcullis.destroy(
                        function(resp) {
                            if ('errors' in resp) {
                                self.error(resp['errors']);
                                return;
                            }
                            else if ('success' in resp) {
                                self.remove_row(selected);
                                self.success(resp.success);
                                self.clear_row_selection();
                            }
                            else
                                self.error('Unknown error has occurred on delete.');
                        },
                        {'model_name': self.model_name, 'data': self.model.getItem(selected)}
                    );
                };
                confirm_dialog('delete_confirm', 'Delete', delete_func);//, function(){return;});
            }
            else {
                this.remove_row(selected);
                this.success('Locally removed row: ' + selected + '.');
            }
        };
        
        /** Stuff to do on error. */
        this.error = function(msg) {
            $('#error_msg').text(msg);
            confirm_dialog('error_dialog', null, null, "Ok", function() {
                $('#error_msg').text('');
            }, false);
        };

        /** Stuff to do on success. */
        this.success = function(msg) {
            console.log('Success: ' + msg);
            $('#server_messages').html(msg).css('color','green');
        };

        /** Here we initialize our object. */
        this.init = function() {
            this.model_name = $('#model_name').val();
            self = this;
            Dajaxice.portcullis.get_columns(
                function(resp) { 
                    self.columns = resp;

                    // Add editors to columns
                    for ( var i = 0; i < self.columns.length; i++) {
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
                            case 'm2m':
                                self.columns[i].formatter = m2m_formatter;
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
                    $(refresh_button).appendTo(self.grid.getTopPanel());
                    $(message_span).appendTo(self.grid.getTopPanel());
                    
                    self.grid.setSelectionModel(new Slick.RowSelectionModel());

                    /*
                    self.grid.onCellChange.subscribe(function (e, args) {
                        args.item._isNotEdited = false;
                    });*/

                    self.grid.getSelectionModel().onSelectedRangesChanged.subscribe(function(e, args) {
                        var panel = self.grid.getTopPanel();
                        var serv_msg = $('#server_messages'); 

                        //Add delete button if it's not in panel            
                        if($(panel).has('input[value="Delete"]').length <= 0)
                            $(serv_msg).before(delete_button);
                        
                        //Add edit button if it's not in panel            
                        if($(panel).has('input[value="Edit"]').length <= 0)
                            $(serv_msg).before(edit_button);

                        $(serv_msg).html('');
                    });

                    self.refresh();
                },
                {'model_name': self.model_name}
            );
        };
       
        this.clear_row_selection = function() {
            var panel = this.grid.getTopPanel();
            $(panel).find('input[value="Delete"]').remove(); 
            $(panel).find('input[value="Edit"]').remove(); 
            this.grid.resetActiveCell(); 
        };        

        this.init();
    }

    /** Use this function to pop up a modal dialog asking for user input.
     * Argurments action, action_func, cancel_func are optional.
     */
    function confirm_dialog(id, action, action_func, cancel, cancel_func, destroy)
    {
        if (!cancel)
            cancel = 'Cancel';

        buttons = [{
            text: cancel,
            click: function() {
                if ( cancel_func )
                    cancel_func();
                $(this).dialog('destroy');
                if(destroy)
                    $('#'+id).remove();
            }
        }];

        if ( action ) {
            buttons.push({
                text: action,
                click: function() {
                    if ( action_func )
                        action_func();
                    $(this).dialog('destroy');
                    if(destroy)
                        $('#'+id).remove();
                }
            });
        }

        $('#' + id).dialog({
            autoOpen: true,
            resizable: true,
            hide: "fade",
            show: "fade",
            modal: true,
            minWidth: 250,
            maxWidth: 1000,
            minHeight: 200,
            maxHeight: 1000,
            height: 500,
            width: 500,
            dialogClass: "confirmation dialogue",
            buttons: buttons
        });
    }

    /** Custom formatter for Foreign Key columns in the data grid */
    function foreign_key_formatter(row, cell, columnDef, dataContext) {
        var grid = myGrid.grid;
        var model = myGrid.model;
        var col = grid.getColumns()[cell]['field'];
        var data = model.get_cell_data(row, col);
        return data['__unicode__'];
    }

    /** Custom formatter for Many to Many columns in the data grid */
    function m2m_formatter(row, cell, columnDef, dataContext) {
        var grid = myGrid.grid;
        var model = myGrid.model;
        var col = grid.getColumns()[cell]['field'];
        var data = model.get_cell_data(row, col);
        
        var m_input = ""; 
        if(data.length > 0) {
            //Create div used for dialog when viewing m2m data
            var div = "<div id='m2m_"+row+"_"+cell+"' style='display:none'>";
            
            var ul = "<ul>";
            for (var i = 0; i < data.length; i++) {
                var li = "<li>"+data[i]['__unicode__']+"</li>";
                ul += li;
            };
            ul += "</ul>";
            div += ul + "</div>"; 
            
            //Make button that triggers dialog
            var onclick = "confirm_dialog('m2m_" + row + "_" + cell + "', null, null, 'Ok');";
            m_input = '<input type="button" value="View" onclick="' + onclick + '" />' + div;
        }

        return m_input;
    }

    $.extend(window, {
        'DataGrid': DataGrid,
        'confirm_dialog': confirm_dialog,
    });

    /** Returns a html div with inputs to be used in a dialog for the grid add button. 
     * 
     *  Keyword Args
     *      columns - The DataGrids columns object.
     *      record  - Dict containing data that will be pre-inserted into the input fields.
     *
     *  Return: Dict with the html div and it's id or null if no columns are editable.
     *          {
     *              'div': The html div,
     *              'id': The div's id
     *          }
     * */
    function get_grid_form(columns, record) 
    {
        var dict = {'id': myGrid.model_name+"_add"};
        var div = "<div id='"+myGrid.model_name+"_add'>" 
        var ul = "<ul style='list-style: none'>";
     
        //If we cycle through all columns and none are editable we'll return null
        var model_editable = false;
        $.each(columns, function(i, col) {
            //continue if can't edit this one
            if (!col._editable)
               return true;
            else
                model_editable = true;     
    
            var li = "<li style='margin-top: 1em'>";
            var span = "<span class='field' style='display: none'>"+col.field+"</span>";
            var input = col.name+":";
            var value = ""
            if (record)
                value = record[col.field]
            switch(col._type) {
                case 'integer':
                    input += span + "<input class='add_form_input' type='text' value='"+value+"'/>"; 
                    break;
                
                default:
                    input += span + "<input class='add_form_input' type='text' value='"+value+"' />";  
            }

            li += input + "</li>";
            ul += li;
        });
        div += ul + "</ul></div>";
        dict['div'] = div;

        if (!model_editable)
            return null;
        return dict;
    } 

    /** Callback method for when user clicks add button in add new record dialog */
    function add_record_callback() 
    {
        var new_row = {};
        $('.add_form_input').each(function(i, input) {
            var field = $(input).prev('span.field').text();
            new_row[field] = $(input).val(); 
        });

        myGrid.add_row(new_row);
    }

    function edit_record_callback (index) 
    {
        var edited_row = {};
        $('.add_form_input').each(function(i, input) {
            var field = $(input).prev('span.field').text();
            edited_row[field] = $(input).val(); 
        });

        myGrid.add_edited_row(edited_row, index);
    }

})(jQuery);

