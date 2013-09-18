$(function() {
    var Sensor = $.fn.Sensor;

    function DataStream() {
        this.owner = ko.observable();
        this.sensor = ko.observable(new Sensor());
        this.name = ko.observable();

        this.list = {};

        this.init = function(vars) {
            vars = vars || {};
            this.owner(vars.owner);
            this.name(vars.name);
            if(vars.hasOwnProperty('sensor')) {
                var newSensor = new Sensor();
                newSensor.init(vars.sensor);
                this.sensor(newSensor);
            }
        }.bind(this);
        
    }

    $.fn.DataStream = DataStream;
});
