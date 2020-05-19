$(document).ready(main());

function main() {
    $('#id_app_date').attr('autocomplete',"off").datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
    });
    $('#id_service')[0].addEventListener('change', service_ajax_request);
    try {
        $('#id_num_client_n')[0].addEventListener('change',dossier_ajax_request);

    }
    catch (e) {
        $('#id_num_client_j')[0].addEventListener('change',dossier_ajax_request);
    }
    
}


function dossier_ajax_request(event) {
    var client = $('#id_num_client_n');
    if (client[0] !== undefined)
        $.ajax({
                type: "POST",
                async: true,
                url: '/database/sendClient/',
                data: {
                    csrfmiddlewaretoken: getCookie('csrftoken'),
                    client: client.val(),
                    dosJ: false
                },
                success: updateN,
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log(textStatus, errorThrown);
                }
            });
    else {
        client = $('#id_num_client_j');

        $.ajax({
            type: "POST",
            async: true,
            url: '/database/sendClient/',
            data: {
                csrfmiddlewaretoken: getCookie('csrftoken'),
                client: client.val(),
                dosJ: true
            },
            success: updateJ,
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });
    }
}
function updateN(data){
    var dossier = $('#id_code_dossier_n');
    dossier.empty();
    dossier.append(`<option value="" selected="">---------</option>`);
    for (var item in data['dossier']){
        dossier.append(`<option value="${data['dossier'][item].code}">${data['dossier'][item].code}</option>`)
    }
}
function updateJ(data){
    var dossier = $('#id_code_dossier_j');
    dossier.empty();
    dossier.append(`<option value="" selected="">---------</option>`);
    for (var item in data['dossier']){
        dossier.append(`<option value="${data['dossier'][item].code}">${data['dossier'][item].code}</option>`)
    }
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
    var lawyer_block = $('#id_lawyer_code');
    lawyer_block.empty();
    lawyer_block.append(`<option value="" selected="">---------</option>`)
    for (var item in data['lawyers']){
        lawyer_block.append(`<option value="${data['lawyers'][item].lawyer_code}">
                            ${data['lawyers'][item].lawyer_code} : ${data['lawyers'][item].spec}</option>`)
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