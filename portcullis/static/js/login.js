function login() 
{
    var post_data = new Object();
    post_data['username'] = $('#username').val();    
    post_data['password'] = $('#password').val();    

    if(username == '') {
        $('#login_error').text('Please provide a user name.');
        return;
    }

    var json_data = JSON.stringify(post_data);
    var csrf = $('input[name="csrfmiddlewaretoken"]').val();
    var data = {
                  'json_data': json_data,
        'csrfmiddlewaretoken': csrf
    };

    $.post('/portcullis/login/', data, post_login);
}

function post_login(data)
{
    $('#side_pane_content').html(data.streams_html);
    $('#greeting').html(data.greeting);
}


