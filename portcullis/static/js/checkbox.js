function checkOwned(source) 
{
  checkboxes = document.getElementsByName('owned');
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}

function checkPublic(source) 
{
  checkboxes = document.getElementsByName('public');
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}

function checkView(source) 
{
  checkboxes = document.getElementsByName('view');
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}
