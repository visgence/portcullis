function checkPrivate(source) 
{
  checkboxes = document.getElementsByName('private');
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}

function checkPublic(source) 
{
  checkboxes = document.getElementsByName('public');
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}