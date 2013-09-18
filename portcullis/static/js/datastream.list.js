$(function() {
    var DataStream = $.fn.DataStream;

    function DataStreamList() {

        this.dataStreams = ko.observableArray();
        this.streamUri = '';
        this.tableMsg = ko.observable();

        this.init = function(vars) {
            vars = vars || {};
            if(!vars.hasOwnProperty('streamUri') || vars['streamUri'] === '')
                throw('No DataStream URI was given.');

            this.streamUri = vars['streamUri'];
            this.dataStreams([]);
        }.bind(this);

        this.addStream = function(data) {
            var newStream = new DataStream();
            newStream.init(data);
            newStream.list = this;
            this.dataStreams.push(newStream);
        }.bind(this);

        this.loadclaimed = function() {
            var self = this;
            $.get(this.streamUri, function(resp) {
                if(resp.errors.length > 0) {
                    console.error(resp);
                    self.tableMsg("Something went wrong loading your datastreams.");
                }
                else {
                    self.tableMsg("");
                    self.dataStreams.removeAll();
                    $.each(resp.streams, function() {
                        self.addStream(this);
                    });
                };
            }).
            fail(function(resp) {
                console.error(resp);
                var error = JSON.parse(resp.responseText);
                if(error.errors.length > 0) {
                    self.tableMsg("Something went wrong loading your datastreams.");
                }
            });
        }.bind(this);

        this.refresh = function() {
            this.loadclaimed();
        }.bind(this);

    }
    
    $.fn.DataStreamList = DataStreamList;
});
