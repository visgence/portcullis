$(function() {
    var Sensor = $.fn.Sensor;

    function DataStream() {
        this.id = ko.observable();
        this.owner = ko.observable();
        this.sensor = ko.observable(new Sensor());
        this.name = ko.observable();
        this.readingUri = ko.observable();

        this.list = {};

        this.init = function(vars) {
            vars = vars || {};
            this.id(vars.id);
            this.owner(vars.owner);
            this.name(vars.name);

            if(!vars.hasOwnProperty('readingUri') || vars['readingUri'] === '')
                throw('No Sensor Reading URI was given.');
            
            this.readingUri(vars.readingUri);

            if(vars.hasOwnProperty('sensor')) {
                var newSensor = new Sensor();
                newSensor.init(vars.sensor);
                this.sensor(newSensor);
            }
        }.bind(this);
       
        this.dataUrl = ko.computed(function() {
            return window.location.origin+this.readingUri()+this.id()+'/';
        }.bind(this));
    }

    $.fn.DataStream = DataStream;
});
