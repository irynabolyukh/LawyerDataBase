$(document).ready(main());

function main() {
    addDatePicker()

}


function addDatePicker() {
    console.log("auf")
    $('#date1').datepicker({
        dateFormat: "d/m/yy",
        changeMonth: true,
        changeYear: true,
        onSelect: getStats,
    });
    $('#date2').datepicker({
        dateFormat: "dd/mm/yy"
    });

}

function getStats(date) {
    arrayDate = date.split('/');
    day = arrayDate[0];
    month = arrayDate[1];
    year = arrayDate[2];
    $.ajax({
        type: "POST",
        async: true,
        url: '/database/getstats/',
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            day : day,
            month : month,
            year : year,

        },
        success: function(data){
            console.log(data)
        }
    })
}

function getDates() {
    $('#date1')
    $('#date2')
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}