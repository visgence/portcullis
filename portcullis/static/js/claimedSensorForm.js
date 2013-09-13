
$(function() {

    var init = function(url, email) {

        var vm = new $.fn.ClaimedSensorList();
        vm.init({'owner': email, 'sensorUri': url});
        vm.loadclaimed();
        ko.applyBindings(vm, $('#sensor-registration').get(0)); 

        //TODO: move this stuff into ClaimedSensor
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
        
        $('#sensor-claim-form').on('submit', function() {
       
            var data = {
                'email': email
                ,'sensors': [{'uuid': $('#uuid').val(), 'name': $('#name').val()}]
            };
           
            $.post(url, JSON.stringify(data), function(resp) {
                console.log(resp);
                if(resp.errors.length > 0)
                    handleErrors(resp.errors);
                else if(resp.sensors.length > 0 && resp.sensors[0].uuid === data.sensors[0].uuid) {
                    vm.loadclaimed();
                    resetMsgs();
                    $('#sensor-claim-form').get(0).reset();
                    $('#form-msg').text("Sensor claimed successfully!").closest('div.form-group').addClass('has-success');
                }
                else
                    handleErrors(["We're sorry, but an unexpected error occureced."]);
            });

            //Stop form from actually submiting
            return false;
        });
    };

    $.fn.ClaimedSensorForm = {
        'init': init
    };
});
