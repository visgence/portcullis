
$(function() {


    var SensorForm = function() {
        this.sensorToAdd = ko.observable();
        this.sensorList = new $.fn.SensorList();

        this.sensorUri = '';
        this.owner = '';

        this.formMsg = ko.observable();
        this.hasError = ko.observable();

        this.init = function(vars) {
            vars = vars || {};
            if(!vars.hasOwnProperty('sensorUri') || vars['sensorUri'] === '')
                throw('No Sensor URI was given.');
            if(!vars.hasOwnProperty('owner') || vars['owner'] === '')
                throw('No owner was given.');

            this.sensorUri = vars['sensorUri'];
            this.owner = vars['owner'];

            this.hasError(false);

            this.sensorList.init({'owner': this.owner, 'sensorUri': this.sensorUri});
            this.sensorList.loadclaimed();
            ko.applyBindings(this.sensorList, $('#users-claimed-sensors').get(0));
            
            this.sensorToAdd(new $.fn.Sensor());
        }.bind(this);

        var handleErrors = function(errors) {
            console.error(errors);
            var self = this; 
            self.hasError(true);
            self.formMsg("An unexpected error occured");
        }.bind(this);

        this.claimSensor = function() {
            this.formMsg('');
            if(!this.sensorToAdd().isValid())
                return;

            var data = {
                'email': this.owner
                ,'sensors': [this.sensorToAdd().toDict()]
            };
          
            var self = this;
            $.post(this.sensorUri, JSON.stringify(data), function(resp) {
                if(resp.errors.length > 0)
                    handleErrors(resp.errors);
                else if(resp.sensors.length > 0 && resp.sensors[0].uuid === data.sensors[0].uuid) {
                    self.sensorList.loadclaimed();
                    self.sensorToAdd().reset();
                    self.hasError(false);
                    self.formMsg("Sensor claimed successfully!");
                }
                else
                    handleErrors(["We're sorry, but an unexpected error occureced."]);
            })
            .fail(function(resp) {
                handleErrors([resp.responseText]);   
            });
        }.bind(this);
    };


    $.fn.SensorForm = SensorForm;
});
