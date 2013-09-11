

$(function() {

    var Sensor = function(){
        this.uuid = ko.observable();
        this.name = ko.observable();

        this.init = function(vars) {
            vars = vars || {};
            this.uuid(vars.uuid);
            this.name(vars.name);
        };
    }.bind(this);

    var SensorViewModel = function() {
        this.registeredSensors = ko.observableArray();

        //TODO: Make this it's own user class
        this.owner = '';
        this.sensorUri = '';

        this.init = function(vars) {
            vars = vars || {};
            this.owner = vars.owner || '';
            this.sensorUri = vars.sensorUri || '';
            this.registeredSensors([]);
        };

        this.addSensor = function(data) {
            var newSensor = new Sensor();
            newSensor.init(data);
            this.registeredSensors.push(newSensor);
        };

        this.loadRegistered = function() {
            var self = this;
            $.get(this.sensorUri, {'credentials': JSON.stringify({'email': this.owner})}, function(resp) {
                self.registeredSensors.removeAll();
                $.each(resp.sensors, function() {
                    self.addSensor(this);
                });
            });
        };

    }.bind(this);

    var init = function(url, email) {

        var vm = new SensorViewModel();
        vm.init({'owner': email, 'sensorUri': url});
        vm.loadRegistered();
        ko.applyBindings(vm, $('#sensor-registration').get(0)); 
   

        //TODO: move this stuff into view model
        var resetMsgs = function() {
            $('#uuid-msg').text('').closest('div.form-group').removeClass('has-error');
            $('#name-msg').text('').closest('div.form-group').removeClass('has-error');
            $('#form-msg').text('').closest('div.form-group').removeClass('has-error has-success');
        };

        var handleErrors = function(errors) {
            resetMsgs();
            $.each(errors, function(i, error) {
                if(error.hasOwnProperty('name'))
                    $('#name-msg').text(error['name']).closest('div.form-group').addClass('has-error');
                else if(error.hasOwnProperty('uuid'))
                    $('#uuid-msg').text(error['uuid']).closest('div.form-group').addClass('has-error');
                else
                    $('#form-msg').text(error).parent('div.form-group').addClass('has-error');
            });
        };
        
        $('#sensor-register-form').on('submit', function() {
       
            var data = {
                'email': email
                ,'sensors': [{'uuid': $('#uuid').val(), 'name': $('#name').val()}]
            };
           
            $.post(url, JSON.stringify(data), function(resp) {
                console.log(resp);
                if(resp.errors.length > 0)
                    handleErrors(resp.errors);
                else if(resp.sensors.length > 0 && resp.sensors[0].uuid === data.sensors[0].uuid) {
                    vm.loadRegistered();
                    resetMsgs();
                    $('#sensor-register-form').get(0).reset();
                    $('#form-msg').text("Sensor registered successfully!").closest('div.form-group').addClass('has-success');
                }
                else
                    handleErrors(["We're sorry, but an unexpected error occureced."]);
            });

            //Stop form from actually submiting
            return false;
        });
    };

    $.fn.Sensor = {
        'init': init
    };
});
