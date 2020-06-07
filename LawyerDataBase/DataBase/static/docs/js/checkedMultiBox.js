$(document).ready(main());

function main(){
    getLawyers()

}

function getLawyers(){
    service = $('#id_service_code').val()
     $.ajax({
                type: "POST",
                async: true,
                url: '/database/lawyerServiceCode/',
                data: {
                    csrfmiddlewaretoken: getCookie('csrftoken'),
                    service: service,
                },
                success: setCheckBoxes,
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log(textStatus, errorThrown);
                }
            });
}

function setCheckBoxes(data) {
    lawyerList = $('input[type=checkbox]')
    for (lawyer of lawyerList){
        if (data['lawyers'].includes($(lawyer).attr("value")))
            $(lawyer).prop('checked', true);
    }

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