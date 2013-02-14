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

/** Setup the model kendo datasource. */

var dataSource = new kendo.data.DataSource({
    error: function(e) {
        alert(e.errors);
        var grid = $('#{{model_name}}_grid').data('kendoGrid');
        grid.cancelChanges();
    },
    transport: {
        read: function(options){
            console.log('In read');
            Dajaxice.portcullis.read_source(function(response) {
                options.success(response);}, { 'model_name': '{{model_name}}'});
        },
        update: function(options){
            Dajaxice.portcullis.update_model_obj(function(response) {
                options.success(response);}, {'data': options.data, 'model_name':'{{model_name}}'});
        },
        destroy: function(options){
            Dajaxice.portcullis.destroy(function(response) {
                options.success(response);
            }, {'data':options.data});   
        },
        create: function(options) {
            Dajaxice.portcullis.create_model_obj(function(response) {
                options.success(response);}, {'data': options.data, 'model_name': '{{model_name}}'});
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
            return d;
        },
        errors: function(response) {
            return response.errors;
        },
        model: {{ model|safe }}
    }
}); 

$(function() {    
    $('#{{model_name}}_grid').kendoGrid({
        dataSource: dataSource,
        columns: {{ columns|safe }},
        editable: 'popup',
        navigable: true,
        toolbar: ['create'],//, 'save', 'cancel'],
        //editable: {
        //    update: true,
        //    destroy: false,
        //    confirmation: "Do you really want to delete this item?  This operation cannot be undone."
        //},
        navigatable: true,
        sortable: true
    });
});
