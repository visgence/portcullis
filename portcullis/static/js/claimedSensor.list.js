$(function() {

    var ClaimedSensorList = function() {

        this.claimedSensors = ko.observableArray();

        //TODO: Make this it's own user class
        this.owner = '';
        this.sensorUri = '';

        this.init = function(vars) {
            vars = vars || {};
            this.owner = vars.owner || '';
            this.sensorUri = vars.sensorUri || '';
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
            $.get(this.sensorUri, function(resp) {
                if(resp.errors.length > 0) {
                    $('#table-error-msg').text("Something went wrong loading your claimed sensors.");
                }
                else {
                    $('#table-error-msg').text('');
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
                    $('#table-error-msg').text("Something went wrong loading your claimed sensors.");
                }
            });
        }.bind(this);

        this.refresh = function() {
            this.loadclaimed();
        }.bind(this);

    };

    $.fn.ClaimedSensorList = ClaimedSensorList;
});
