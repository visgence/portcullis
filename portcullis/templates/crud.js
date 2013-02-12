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
$(function() {
    dataSource = new kendo.data.DataSource({
        transport: {
            read: {
                url: 'read/'
            },
            update: {
                url: 'update/',
                type: 'post/'
            },
            destroy: {
                url: 'destroy/',
                type: 'post/'
            },
            create: {
                url: 'create/',
                type: 'post'
            },
            parameter: function(data, type) {
                return {data: kendo.stringify(data)};
            }
        },
        schema: {
            data: function(d) {
                return d.map(function(e) {
                    data = e['fields'];
                    data['id'] = e['pk'];
                    return data;
                });
            },
            model: {{ model|safe }}
        }
    }); 
    
    $('#ds_grid').kendoGrid({
        dataSource: dataSource,
        columns: {{ columns|safe }},
        editable: 'popup',
        navigable: true,
        toolbar: ['create']
    });
});