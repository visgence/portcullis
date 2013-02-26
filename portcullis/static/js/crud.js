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
            add_data: function(row, i) {
                this.data.splice(i, 0, row); 
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

            var add_form = get_grid_form(this.columns, null, 'Add Record');
            if (add_form) {
                var add_callback = function() {record_callback(0, false);};

                $('#'+this.model_name+'_grid').append(add_form.div);

                confirm_dialog(add_form.id, 'Add', add_callback, 'Cancel', null, true);
            }
            else
                console.log('no editable columns');
        };

        /** Method to edit a selected record in the grid. */
        this.edit_record = function() {
            var selected_index = this.grid.getSelectedRows();
            var selected_row = this.model.getItem(selected_index);

            var edit_form = get_grid_form(this.model_name+'_grid', this.columns, selected_row, 'Edit Record');
            if (edit_form) {
                var edit_callback = function() {record_callback(selected_index, true);};

                //$('#'+this.model_name+'_grid').append(edit_form.div);

                confirm_dialog(edit_form.id, 'Save', edit_callback, 'Cancel', null, true);
            }
            else
                this.error('This grid is not editable.');
        };

        /** Method to add a row to the grid.
         *
         *  The row will either be added to the grid as a new row or
         *  will replace an existing row specified at the given index
         *  if updating is true.
         *
         * Keyword Args
         *    row      - Dictionary that will put into the grid as a row.
         *    index    - Row position for the row to be inserted into.
         *    updating - Boolean, row will replace the row in grid at index if true
         *               and will be inserted at index if false.
         */
        this.add_row = function(row, index, updating) {
            self = this;
          
            //Need pk if updating to know which object to update
            if(updating)
                row['pk'] = self.model.get_pk(index);

            self.save_row(index, row, updating);
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
                    $('#'+self.model_name + '_add').dialog('close');
                    //Either add new row to beginning or update one.
                    if (update) {
                        self.model.setItem(i, resp[0]);
                        self.grid.invalidateRow(i);
                    }
                    else {
                        self.model.add_data(resp[0]);
                        self.grid.invalidateAllRows();
                    }
                    
                    self.grid.render();
                    self.success('Updated row ' + i);
                }
                self.clear_row_selection();
            };
        };

        /** Saves or updates a specified row at a given index
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
 
        /** Removes a row from the grid at a given index
         *
         *  Keyword Args
         *      index - The index to remove the row from.*/
        this.remove_row = function(index) {
            this.model.remove_data(index);
            this.grid.invalidate();
        };

        /** Deletes a selected row from the grid and removes that object from the database. */
        this.delete_row = function() {
            // get the selected row, right now assume only one.
            var selected = this.grid.getSelectedRows();
            if (selected.length != 1) {
                this.error("Error, we don't have exactly 1 data item selected!");
                return;
            }

            var row = this.model.getItem(selected[0]);

            // If there is an id, send an ajax request to delete from server, otherwise, just
            // remove it from the grid.
            if ('pk' in row) {
                self = this;
                var delete_func = function() {
                    Dajaxice.portcullis.destroy(
                        function(resp) {
                            if ('errors' in resp) {
                                self.error(resp['errors']);
                                return;
                            }
                            else if ('success' in resp) {
                                $('#delete_confirm').dialog('close');
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
                confirm_dialog('delete_confirm', 'Delete', delete_func);
            }
            else {
                this.remove_row(selected);
                this.success('Locally removed row: ' + selected + '.');
            }
        };
       
        /** Shows a dialog to the user for the given error message.
         *
         * Keyword Args
         *    msg - Error message as a string.
         */
        this.error = function(msg) {
            console.log('Error: ' + msg);
            var error_div = $('#error_dialog').clone();
            $(error_div).attr('id', 'error_dialogue_message');
            var dlg_msg = $('#dialogue_message')
            if ( dlg_msg.length >= 1) {
                var msg_html = $(dlg_msg).html(error_div);
                $('#error_dialogue_message #error_msg').text(msg);
                $('#error_dialogue_message').css('display', 'inline');
                $('#dialogue_message').parent().animate({scrollTop: 0}, 'fast');
            }
            else {
                $('error_dialog').text(msg);
                confirm_dialog('error_dialog', null, null, "Ok", function() {
                    $('#error_msg').text('');
                }, false);
            }
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
                                    self.columns[i].formatter = Slick.Formatters.Checkmark;
                                    break;
                                case 'foreignkey':
                                    self.columns[i].formatter = foreign_key_formatter;
                                    break;
                                case 'm2m':
                                    self.columns[i].formatter = m2m_formatter;
                                    break;

                                case 'number':
                                case 'char':
                                case 'integer':
                                case 'text':
                                case 'date':

                                default:
                            }
                        }
                    }
                        
                    self.grid = new Slick.Grid("#" + self.model_name + "_grid", self.model, self.columns, self.options);

                    // Add controls
                    $(add_button).appendTo(self.grid.getTopPanel()); 
                    $(refresh_button).appendTo(self.grid.getTopPanel());
                    $(message_span).appendTo(self.grid.getTopPanel());
                    
                    self.grid.setSelectionModel(new Slick.RowSelectionModel());

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

                    self.grid.onDblClick.subscribe(function(e, args) {
                        self.edit_record();
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
                    /*$(this).dialog('destroy');
                    if(destroy)
                        $('#'+id).remove();*/
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
            close: function() {
                if ( cancel_func )
                    cancel_func();
                $(this).dialog('destroy');
                if(destroy)
                    $('#' + id).remove();
            },  
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
     *      id      - The id of the dom element to append the div after.
     *      columns - The DataGrids columns object.
     *      record  - Dict containing data that will be pre-inserted into the input fields.
     *      title   - String to put into the title bar of dialog when created.
     *
     *  Return: Dict with the html div and it's id or null if no columns are editable.
     *          {
     *              'div': The html div,
     *              'id': The div's id
     *          }
     * */
    function get_grid_form(id, columns, record, title) 
    {
        var dict = {'id': myGrid.model_name+"_add"};
        var div = $("<div></div>")
            .attr("id", myGrid.model_name+'_add')
            .attr('title', title);
        var ul = $("<ul></ul>").css("list-style", "none");

        var msg_div = $('<div></div>').attr('id',  'dialogue_message');
        $(div).append(msg_div);
       
        $('#'+id).append(div);
        div.append(ul);

        //If we cycle through all columns and none are editable we'll return null
        var model_editable = false;
        $.each(columns, function(i, col) {
            
            //continue if can't edit this one
            if (!col._editable)
               return true;
            else
                model_editable = true;     
   
            //Set up html containers for the input
            var li = $("<li></li>").css('margin-top', '1em');
            ul.append(li);
            

            var span = $("<span></span>")
                .attr('class', 'field')
                .css('display', 'none')
                .text(col.field);

            var label = $("<span></span>").text(col.name);
            var input = null;
            var value = "";

            //If updateing then we'll set the field with the current value
            if (record)
                value = record[col.field];
            
            switch(col._type) {
                case 'integer':
                    input = $("<input/>")
                        .val(value)
                        .attr({ 
                            'class': 'add_form_input',
                            'type' : 'text' 
                        });
                    li.append(input);
                    input.before(label);
                    $(input).spinner();
                    input.before(span);
                    break;
               
                //Build a select field with options for any foreign keys
                case 'foreignkey': 
                    input = $("<select></select>")
                        .attr({'class': 'add_form_input foreignkey'});

                    //Get all objects that the user can select from
                    Dajaxice.portcullis.read_source( function(resp) {

                        $(resp).each(function(i, obj) {
                            var option = $("<option></option>")
                                .attr('class', obj.pk)
                                .text(obj.__unicode__);

                            if(value != '' && obj.pk == value.pk) 
                                option.attr('selected', 'selected');
                            input.append(option);

                        });
                    }, {'model_name': col.model_name}); 
                    li.append(input);
                    input.before(label);
                    input.before(span);
                    break;
                
                //Build select multiple for many-to-many fields and their objects.
                case 'm2m':
                    input = $("<select></select>")
                        .attr({
                            'class'   : 'add_form_input m2m',
                            'multiple': 'multiple'
                        });
                    
                    //Get all objects that the user can select from
                    Dajaxice.portcullis.read_source( function(resp) {

                        $(resp).each(function(i, obj) {
                            var option = $("<option></option>")
                                .attr('class', obj.pk)
                                .text(obj.__unicode__);

                            //Pre-select appropriate objects
                            $(value).each(function(i, val) {
                                if(val != '' && obj.pk == val.pk) 
                                    option.attr('selected', 'selected');
                            });

                            input.append(option);
                        });
                    }, {'model_name': col.model_name});
                    li.append(input);
                    input.before(label);
                    input.before(span);
                    break;

                case 'datetime':
                    input = $("<input/>")
                        .val(value)
                        .attr({ 
                            'class': 'add_form_input',
                            'type' : 'text' 
                        });
                    li.append(input);
                    input.before(label);
                    input.before(span);
                    $(input).datetimepicker({
                        showSecond: true,
                        dateFormat: 'mm/dd/yy',
                        timeFormat: 'hh:mm:ss',
                    });
                    $(input).datetimepicker('setDate', value); 
                    break;
              
                default:
                    input = $("<input/>")
                        .val(value)
                        .attr({ 
                            'class': 'add_form_input',
                            'type' : 'text' 
                        });
                    li.append(input);
                    input.before(label);
                    input.before(span);
            }
        });

        dict['div'] = div;
        
        if (!model_editable)
            return null;
        return dict;
    }
 
    /** Callback method for when a user adds or updates a record
     *
     * Keyword Args
     *    index    - The index where the record will be added/edited.
     *    updating - Boolean, true if updating a record and false if adding one.
     */
    function record_callback(index, updating) 
    {
        var row = {};
        $('.add_form_input').each(function(i, input) {

            var field = $(input).prev('span.field').text();
            if($(input).hasClass('foreignkey')) {
                row[field] = {'pk': $(':selected', input).attr('class')};
            }
            else if($(input).hasClass('m2m')) {
                row[field] = new Array();
                $(':selected', input).each(function(i, sel) {
                    row[field].push({'pk': $(sel).attr('class')});
                });
            }
            else
                row[field] = $(input).val(); 
        });

        myGrid.add_row(row, index, updating);
    }

})(jQuery);

