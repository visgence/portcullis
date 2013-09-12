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
    }
}


/** This method will pop up a dialog that will allow the user to change their password.
  *
  */
function changePassDialog()
{
    var ok = {
        text: 'OK',
        click: function() {
            $(this).dialog('close');
        }
    };

    var buttons = [
        {
            text: 'Change Password',
            click: function() {
                // Send the change password request
                var postData = {};
                var self = this;

                postData.oldPassword = $('#oldPassword').val();
                postData.newPassword = $('#passwordInput').val();

                if ( postData.oldPassword === '' ) {
                    makeDialog('Please enter your old password', 'Error', [ok]);
                    return;
                }
                if ( postData.newPassword === '' ) {
                    makeDialog('Please enter your new password', 'Error', [ok]);
                    return;
                }
                if ( postData.newPassword !== $('#passwordReinput').val() ) {
                    makeDialog('Your new passwords do not match.  Please reenter them.', 'Error', [ok]);
                    return;
                }
                var csrf = $('input[name="csrfmiddlewaretoken"]').val();
                $.post('/api/changePassword/', {csrfmiddlewaretoken: csrf,
                                                      jsonData: JSON.stringify(postData)},
                       function(resp) {
                           if ( resp.errors ) {
                               makeDialog(resp.errors, 'Error', [ok]);
                           }
                           else if ( resp.success ) {
                               makeDialog(resp.success, 'Success', [ok]);
                               $(self).dialog('close');
                           }
                           else {
                               makeDialog(resp, 'Unknown Error', [ok]);
                           }
                       });
            }
        },
        {
            text: 'Cancel',
            click: function() {
                $(this).dialog('close');
            }
        }
    ];
    
    $.get('/api/passwordForm/', {}, function(resp) {
        if ( resp.errors ) {
            makeDialog(resp.errors, 'Error', [{text:'OK', click: function(){$(this).dialog('close');}}]);
        }
        else if ( resp.html ) {
            makeDialog(resp.html, 'Change Password', buttons);
        }
        else {
            makeDialog(resp, 'Unknown Error', [{text:'OK', click: function(){$(this).dialog('close');}}]);
        }
    });
}
