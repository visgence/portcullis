    
/** Gets the html for managing a users streams and puts it in the content of the page */
function load_model_grid(app, model) 
{
    var url = "/chucho/model_editor/"+app+"/"+model+"/";
    $.get(url, {}, function(data) {
        $('#utilities-container').html(data);  
    });
}
