$(function() {

    var ClaimedSensor = function(){
        this.uuid = ko.observable().extend({required: "UUID is required"});
        this.name = ko.observable().extend({required: "Name is required"});;

        this.list = {};

        this.init = function(vars) {
            vars = vars || {};
            this.uuid(vars.uuid);
            this.name(vars.name);
        }.bind(this);

        this.toDict = function() {
            return {
                'uuid': this.uuid()
                ,'name': this.name()
            };
        };

        this.toJson = function() {
            return JSON.stringify(this.toDict());
        };

        this.isValid = function() {
            var valid = true;
            if(!this.name.isValid())
                valid = false;
            if(!this.uuid.isValid())
                valid = false;
            return valid;
        };

        this.reset = function() {
            this.name.reset();
            this.uuid.reset();
        };
    };

    ko.extenders.required = function(target, msg) {
        target.hasError = ko.observable();
        target.errorMsg = ko.observable();

        //Validates and returns true if observable has an error and false otherwise
        target.isValid = function() {
            validate(target());
            return !target.hasError();
        };

        target.reset = function() {
            target('');
            target.hasError(false);
            target.errorMsg('');
        }

        function validate(newValue) {
            target.hasError(newValue ? false:true);
            target.errorMsg(newValue ? "": msg || "This field is required");
        }

        target.subscribe(validate);
        return target;
    };

    $.fn.ClaimedSensor = ClaimedSensor;
});
