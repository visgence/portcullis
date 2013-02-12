/**
 * portcullis/static/js/crud.js
 *
 * Contributing Authors:
 *    Jeremiah Davis (jdavis@visgence.com)
 *
 * Copyright 2013, Visgence, Inc.
 *
 * This file contains some general helper functions for portcullis.
 */

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
            model: {
                "fields": {
                    "reduction_type": {
                        "editable": true
                    },
                    "description": {
                        "editable": true
                    },
                    "color": {
                        "editable": true
                    },
                    "max_value": {
                        "editable": true
                    },
                    "min_value": {
                        "editable": true
                    },
                    "node_id": {
                        "editable": true
                    },
                    "scaling_function": {
                        "editable": true
                    },
                    "units": {
                        "editable": true
                    },
                    "is_public": {
                        "editable": true
                    },
                    "port_id": {
                        "editable": true
                    },
                    "id": {
                        "editable": false
                    },
                    "name": {
                        "editable": true
                    }
                },
                "id": "id"
            }
        }
    }); 

    $('#ds_grid').kendoGrid({
        dataSource: dataSource,
        columns: [
            {
                "field": "id",
                "title": "id"
            },
            {
                "field": "node_id",
                "title": "node_id"
            },
            {
                "field": "port_id",
                "title": "port_id"
            },
            {
                "field": "units",
                "title": "units"
            },
            {
                "field": "name",
                "title": "name"
            },
            {
                "field": "description",
                "title": "description"
            },
            {
                "field": "color",
                "title": "color"
            },
            {
                "field": "min_value",
                "title": "min_value"
            },
            {
                "field": "max_value",
                "title": "max_value"
            },
            {
                "field": "scaling_function",
                "title": "scaling_function"
            },
            {
                "field": "reduction_type",
                "title": "reduction_type"
            },
            {
                "field": "is_public",
                "title": "is_public"
            }
        ],
        editable: 'popup',
        navigable: true,
        toolbar: ['create']
    });