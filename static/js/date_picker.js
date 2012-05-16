$(document).ready(function()
{
    $('#start').datetimepicker
    ({
        showSecond: true,
        dateFormat: 'yy/mm/dd',
        timeFormat: 'hh:mm:ss tt',
        onSelect: function (selectedDateTime)
        {
            var start = $(this).datetimepicker('getDate');
            $('#end').datetimepicker('option', 'minDate', new Date(start.getTime()));
        }
    });
    $('#end').datetimepicker
    ({
        showSecond: true,
        dateFormat: 'yy/mm/dd',
        timeFormat: 'hh:mm:ss tt',
        onSelect: function (selectedDateTime)
        {
            var end = $(this).datetimepicker('getDate');
            $('#start').datetimepicker('option', 'maxDate', new Date(end.getTime()));
        }
    });

});

