{% comment %}
/**
 * portcullis/static/js/crud.js
 *
 * Contributing Authors:
 *    Evan Salazar   (Visgence, Inc.)
 *    Jeremiah Davis (Visgence, Inc.)
 *
 * Copyright 2013, Visgence, Inc.
 *
 * This file is a template for a dynamic javascript file to setup the 
 * KendoUI grid to manage datastreams.  As long as this file takes to load, I think after development
 * is finished, it should be statically generated.
 */
 {% endcomment %}

/** Setup the DataStream kendo datasource. */

var dataStreamSource = new kendo.data.DataSource({
    error: function(e) {
        alert(e.errors);
        var grid = $('#ds_grid').data('kendoGrid');
        grid.cancelChanges();
    },
    transport: {
        read: function(options){
            console.log('In read');
            Dajaxice.portcullis.read_datastream(function(response) {
                options.success(response);
            });
        },
        update: function(options){
            alert('In update');
        },
        destroy: function(options){
            alert('In destroy');
        },
        create: function(options) {
            Dajaxice.portcullis.create_datastream(function(response) {
                options.success(response);}, {'data': options.data});
        },
        parameter: function(data, type) {
            console.log('In parameter map.');
            console.log(data);
            console.log(type);
            return {data: kendo.stringify(data)};
        }
    },
    schema: {
        data: function(d) {
            console.log('in data');
            var stuff = d.map(function(e) {
                data = e['fields'];
                data['id'] = e['pk'];
                return data;
            });
            console.log(stuff);
            return stuff;
        },
        errors: function(response) {
            return response.errors;
        },
        model: {{ model|safe }}
    }
}); 

var portcullisUserSource = new kendo.data.DataSource({
    transport: {
        read: function(options) {
            Dajaxice.portcullis.read_objects(function(response) {
                options.success(response);
            });
        }
    },
    schema:{
        data: function(d) {
            return d.map(function(e) {
                data = e['fields'];
                data['id'] = e['pk'];
                return data;
            });
        },
        errors: function(response) {
            return response.errors;
        },
        model: {{ user_model|safe }}
    },
    // TODO:  Not currently used.
    customDropDown: function(container, options) {
        $('<input data-text-field="" data-value-field="CategoryID" data-bind="value:' + options.field + '"/>')
            .appendTo(container)
            .kendoDropDownList({
                autoBind: false,
                dataSource: this
            });
    }
});
                                             

$(function() {    
    $('#ds_grid').kendoGrid({
        dataSource: dataStreamSource,
        columns: {{ columns|safe }},
        //editable: 'popup',
        navigable: true,
        toolbar: ['create', 'save', 'cancel'],
        editable: {
            update: true,
            destroy: false,
            confirmation: "Do you really want to delete this item?  This operation cannot be undone."
        },
        navigatable: true,
        sortable: true
    });
});