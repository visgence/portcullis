$(function() {

    var ClaimedSensorList = function() {

        this.claimedSensors = ko.observableArray();

        //TODO: Make this it's own user class
        this.owner = '';
        this.csUri = '';

        this.tableMsg = ko.observable();

        this.init = function(vars) {
            vars = vars || {};
            if(!vars.hasOwnProperty('csUri') || vars['csUri'] === '')
                throw('No Claimed Sensor URI was given.');
            if(!vars.hasOwnProperty('owner') || vars['owner'] === '')
                throw('No owner was given.');

            this.csUri = vars['csUri'];
            this.owner = vars['owner'];
            this.claimedSensors([]);
        }.bind(this);

        this.addSensor = function(data) {
            var newSensor = new $.fn.ClaimedSensor();
            newSensor.init(data);
            newSensor.list = this;
            this.claimedSensors.push(newSensor);
        }.bind(this);

        this.loadclaimed = function() {
            var self = this;
            $.get(this.csUri, function(resp) {
                if(resp.errors.length > 0) {
                    console.error(resp);
                    self.tableMsg("Something went wrong loading your claimed sensors.");
                }
                else {
                    self.tableMsg("");
                    self.claimedSensors.removeAll();
                    $.each(resp.sensors, function() {
                        self.addSensor(this);
                    });
                };
            }).
            fail(function(resp) {
                console.error(resp);
                var error = JSON.parse(resp.responseText);
                if(error.errors.length > 0) {
                    self.tableMsg("Something went wrong loading your claimed sensors.");
                }
            });
        }.bind(this);

        this.refresh = function() {
            this.loadclaimed();
        }.bind(this);

    };

    $.fn.ClaimedSensorList = ClaimedSensorList;
});
