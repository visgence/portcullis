$(function() {

    var ClaimedSensor = function(){
        this.uuid = ko.observable();
        this.name = ko.observable();

        this.list = {};

        this.init = function(vars) {
            vars = vars || {};
            this.uuid(vars.uuid);
            this.name(vars.name);
        }.bind(this);
    };

    $.fn.ClaimedSensor = ClaimedSensor;
});
