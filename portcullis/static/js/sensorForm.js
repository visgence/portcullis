
$(function() {
    
    var DataStreamList = $.fn.DataStreamList;
    var Sensor = $.fn.Sensor;

    function SensorForm() {
        this.sensorToClaim = ko.observable();
        this.streamList = new DataStreamList();

        this.sensorUri = '';
        this.readingUri = '';
        this.user = '';

        this.formMsg = ko.observable();
        this.hasError = ko.observable();

        this.init = function(vars) {
            vars = vars || {};
            if(!vars.hasOwnProperty('sensorUri') || vars['sensorUri'] === '')
                throw('No Sensor URI was given.');
            if(!vars.hasOwnProperty('streamUri') || vars['streamUri'] === '')
                throw('No DataStream URI was given.');
            if(!vars.hasOwnProperty('readingUri') || vars['readingUri'] === '')
                throw('No Sensor Reading URI was given.');
            if(!vars.hasOwnProperty('user') || vars['user'] === '')
                throw('No user was given.');

            this.sensorUri = vars['sensorUri'];
            this.streamUri = vars['streamUri'];
            this.readingUri = vars['readingUri'];
            this.user = vars['user'];

            this.hasError(false);

            this.streamList.init({'owner': this.user, 'streamUri': this.streamUri, 'readingUri': this.readingUri});
            this.streamList.loadclaimed();
            ko.applyBindings(this.streamList, $('#users-claimed-sensors').get(0));
            
            this.sensorToClaim(new Sensor());
        }.bind(this);

        var handleErrors = function(errors) {
            console.error(errors);
            var self = this; 
            self.hasError(true);
            self.formMsg("An unexpected error occured");
        }.bind(this);

        this.claimSensor = function() {
            this.formMsg('');
            if(!this.sensorToClaim().isValid())
                return;

            var data = {
                'email': this.user
                ,'sensors': [this.sensorToClaim().toDict()]
            };
          
            var self = this;
            $.post(this.sensorUri, JSON.stringify(data), function(resp) {
                if(resp.errors.length > 0)
                    handleErrors(resp.errors);
                else if(resp.sensors.length > 0 && resp.sensors[0].uuid === data.sensors[0].uuid) {
                    self.streamList.loadclaimed();
                    self.sensorToClaim().reset();
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
    }

    $.fn.SensorForm = SensorForm;
});
