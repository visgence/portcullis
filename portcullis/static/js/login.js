function login() 
{
    var post_data = {};
    post_data.username = $('#username').val();    
    post_data.password = $('#password').val();    
   
    if(post_data.username === '') {
        $('#login_error').text('Please provide a user name.');
        return;
    }

    var json_data = JSON.stringify(post_data);
    var csrf = $('input[name="csrfmiddlewaretoken"]').val();
    var data = {
                  'json_data': json_data,
        'csrfmiddlewaretoken': csrf
    };

    $.post('/api/login/', data, post_login);
}

function post_login(data)
{
    if(data.error)
        $('#login_error').text(data.error);
    else {
        $('#greeting').html(data.greeting);
        $('#nav').html(data.nav);
        $('#login_error').text('');
        ready_tabs();
    }
}


function changePassDialog()
{

    if(!$('#change-pass-modal').length) {
        
        $.get('/api/passwordForm/', {}, function(resp) {
            
            if ( resp.errors ) {
                sysDialog(resp.errors, "Error", 'error')
            }
            else if ( resp.html ) {
                $(resp.html).modal({
                    backdrop: false
                });

                $('#change-pass-btn').on('click', function() { 
                    $('#pass-msg').removeClass('alert-danger alert').html('');

                    // Send the change password request
                    var postData = {};
                    var self = this;

                    postData.oldPassword = $('#oldPassword').val();
                    postData.newPassword = $('#passwordInput').val();

                    if ( postData.oldPassword === '' ) {
                        $('#pass-msg').addClass('alert-danger alert').html('Please enter your old password');
                        return;
                    }
                    if ( postData.newPassword === '' ) {
                        $('#pass-msg').addClass('alert-danger alert').html('Please enter your new password');
                        return;
                    }
                    if ( postData.newPassword !== $('#passwordReinput').val() ) {
                        var error = 'Your new passwords do not match.  Please reenter them.';
                        $('#pass-msg').addClass('alert-danger alert').html(error);
                        return;
                    }
                    var csrf = $('input[name="csrfmiddlewaretoken"]').val();
                    $.post('/api/changePassword/', {csrfmiddlewaretoken: csrf, jsonData: JSON.stringify(postData)}, function(resp){
                        if ( resp.errors ) {
                            $('#pass-msg').addClass('alert-danger alert').html(resp.errors);
                        }
                        else if ( resp.success ) {
                            $('#change-pass-modal').modal('hide');
                            sysDialog('You have successfully changed your password', 'Success', 'success');
                        }
                        else {
                            $('#pass-msg').addClass('alert-danger alert').html(resp);
                        }
                    });
                    return false;
                });

                $('#change-pass-modal').on('hidden.bs.modal', function() {
                    $('#pass-msg').removeClass('alert-danger alert').html('');
                    $('#change-pass-modal form').get(0).reset();
                });
            }
            else {
                sysDialog(resp, 'Unknown Error', 'error');
            }
        });
    }
    else {
        $("#change-pass-modal").modal('show');    
    }
}

