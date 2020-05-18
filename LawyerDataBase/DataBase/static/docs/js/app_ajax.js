$(document).ready(main());

function main() {
    $('#id_service')[0].addEventListener('change', service_ajax_request);
}


function service_ajax_request(event) {
    services = $('#id_service').val();

    $.ajax({
            type: "POST",
            async: true,
            url: '/database/sendServices/',
            data: {
                csrfmiddlewaretoken: getCookie('csrftoken'),
                services: services

            },
            success: updateServices,
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        })
}

function updateServices(data){
    console.log(data)

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