
$(function() {


    var ClaimedSensorForm = function() {
        this.csToAdd = ko.observable();
        this.csList = new $.fn.ClaimedSensorList();

        this.csUri = '';
        this.owner = '';

        this.formMsg = ko.observable();
        this.hasError = ko.observable();

        this.init = function(vars) {
            vars = vars || {};
            if(!vars.hasOwnProperty('csUri') || vars['csUri'] === '')
                throw('No Claimed Sensor URI was given.');
            if(!vars.hasOwnProperty('owner') || vars['owner'] === '')
                throw('No owner was given.');

            this.csUri = vars['csUri'];
            this.owner = vars['owner'];

            this.hasError(false);

            this.csList.init({'owner': this.owner, 'csUri': this.csUri});
            this.csList.loadclaimed();
            ko.applyBindings(this.csList, $('#users-claimed-sensors').get(0));
            
            this.csToAdd(new $.fn.ClaimedSensor());
        }.bind(this);

        var handleErrors = function(errors) {
            console.error(error);
            var self = this; 
            self.hasError(true);
            self.formMsg("An unexpected error occured");
        }.bind(this);

        this.claimSensor = function() {
            this.formMsg('');
            if(!this.csToAdd().isValid())
                return;

            var data = {
                'email': this.owner
                ,'sensors': [this.csToAdd().toDict()]
            };
          
            var self = this;
            $.post(this.csUri, JSON.stringify(data), function(resp) {
                if(resp.errors.length > 0)
                    handleErrors(resp.errors);
                else if(resp.sensors.length > 0 && resp.sensors[0].uuid === data.sensors[0].uuid) {
                    self.csList.loadclaimed();
                    self.csToAdd().reset();
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


    $.fn.ClaimedSensorForm = ClaimedSensorForm;
});
