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
    var edit_button = '<input type="button" value="Edit" onclick="myGrid.edit_row();"/>';
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
            get_cell_data: function(row, col) {
                return this.data[row][col];
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
                        resp[i]['_isNotEdited'] = true;
                    
                    self.model.set_data(resp);
                    self.grid.invalidate();
                },
                {model_name: self.model_name}
            );
        };

        /** Method to add a record */
        this.add_record = function() {
            //Clear row selection
            this.clear_row_selection();

            var add_form = get_add_form(this.columns);
            if (add_form) {
                $('#'+this.model_name+'_grid').append(add_form.div);
                confirm_dialog(add_form.id, 'Add', add_record_callback, 'Cancel', null, true);
            }
            else
                console.log('no editable columns');
        }

        /** Method to add new row to beginning of grid
         *
         * Keyword Args
         *    new_row - Dictionary containing new row data.
         */
        this.add_row = function(new_row) {
            self = this;
            new_row['_isNotEdited'] = false;
            self.model.prepend_data(new_row);
            self.save_all_rows(); 
            $('#server_messages').html('');
        };

        /** Method to save all the modified rows, checks the _isNotEdited flag */
        this.save_all_rows = function() {
            self = this;
            var noneSaved = true;

            // Go through the models, and if a row has been edited, save it.
            for (var i = 0; i < this.model.getLength(); i++) {
                if (!this.model.getItem(i)._isNotEdited) {
                    console.log('inside');
                    noneSaved = false;
                    var callback = function(index) {
                        var i = index;
                        return function(resp) {
                            if ('errors' in resp) {
                                self.error(resp['errors'])
                                return;
                            }
                            else {
                                self.model.setItem(i, resp[0]);
                                self.model.getItem(i)._isNotEdited = true;
                                self.grid.invalidateRow(i);
                                self.grid.render();
                                self.success('Updated row ' + i);
                            }
                        };
                    };
                    console.log(this.model.getItem(i));
                    Dajaxice.portcullis.update(callback(i),
                                               {'model_name': this.model_name, 'data': this.model.getItem(i)});
                }
            }

            // Nothing to do.
            if ( noneSaved ) {
                $('#server_messages').html('Nothing to save.').css('color', 'green');
                return;
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
            console.log('Error: ' + msg);
            $('#server_messages').html(msg).css('color','red');
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

                    // Add some listeners
                    self.grid.onCellChange.subscribe(function (e, args) {
                        args.item._isNotEdited = false;
                    });

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
                console.log('i canceled');
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

    /** Returns a html div with correct inputs to be used in a dialog for the grid add button. 
     * 
     *  Keyword Args
     *      columns - The DataGrids columns object.
     *
     *  Return: Dict with the html div and it's id or null if no columns are editable.
     *          {
     *              'div': The html div,
     *              'id': The div's id
     *          }
     * */
    function get_add_form(columns) 
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
            switch(col._type) {
                case 'integer':
                    console.log(col._type);
                    input += span + "<input class='add_form_input' type='text'/>"; 
                    break;
                
                default:
                    input += span + "<input class='add_form_input' type='text'/>";  
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

    function add_record_callback() 
    {
        var new_row = {};
        $('.add_form_input').each(function(i, input) {
            var field = $(input).prev('span.field').text();
            new_row[field] = $(input).val(); 
        });

        myGrid.add_row(new_row);
    }

})(jQuery);

