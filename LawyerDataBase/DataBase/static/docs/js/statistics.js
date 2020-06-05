$(document).ready(main());

function main() {
    addDatePicker()

}


function addDatePicker() {
    $('#date1').datepicker({
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        changeYear: true,
        onSelect: getStats,
    });
    $('#date2').datepicker({
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        changeYear: true,
        onSelect: getStats,
    });

}

function getStats(date) {
    date1_elem = $('#date1').removeClass('wrong_input')
    date2_elem = $('#date2').removeClass('wrong_input')


    date1 = date1_elem.datepicker( "getDate" );

    date2 = date2_elem.datepicker( "getDate" );

    if (date1 !== null && date2 !== null) {


    if (date1 < date2) {
        $.ajax({
            type: "POST",
            async: true,
            url: '/database/getstats/',
            data: {
                csrfmiddlewaretoken: getCookie('csrftoken'),
                date1: {
                    day: date1.getDate(),
                    month: String(parseInt(date1.getMonth()) + 1),
                    year: date1.getFullYear(),
                },
                date2: {
                    day: date2.getDate(),
                    month: String(parseInt(date2.getMonth()) + 1),
                    year: date2.getFullYear(),
                }

            },
            success: updateInfo,
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        })
    }
    else{
        date1_elem.val('').addClass('wrong_input')
        date2_elem.val('').addClass('wrong_input')
        // alert("Дата З має бути раніше, за дату ПО")
    }
    }
}

function updateInfo(data) {
    console.log(data);
    $('#won_dossiers')[0].innerHTML = data['all_won_dossiers'];
    $('#closed_dossiers_j')[0].innerHTML = data['closed_j'];
    $('#closed_dossiers_n')[0].innerHTML = data['closed_n'];
    $('#open_dossier_j')[0].innerHTML = data['open_j'];
    $('#open_dossier_n')[0].innerHTML = data['open_n'];
    $('#total_value')[0].innerHTML = data['value'];
    $('.container_past_appointments').remove();
    var given_services =  $('#given_services');
    given_services.find('p').remove();
    var lawyer_service = $('#lawyer_service');
    lawyer_service.find('p').remove();


    if (data['service_count'].length > 0)
        for (var service in data['service_count']){
             given_services
                 .append(
                     `<p><a href="/database/service/${data['service_count'][service].service_code}">
                            ${data['service_count'][service].service_code}</a> <b>${data['service_count'][service].name_service}</b> : 
                         ${data['service_count'][service].count}</p>`)
    }
    else{
        given_services.append("<p>За заданий проміжок не були надані послуги</p>")
    }

    if (data['lawyer_counter'].length > 0)
        for (var lawyer in data['lawyer_counter']){
             lawyer_service
                 .append(
                     `<p><a href="/database/lawyer/${data['lawyer_counter'][lawyer].lawyer_code}">
                        ${data['lawyer_counter'][lawyer].lawyer_code}</a> - <b>
                        ${data['lawyer_counter'][lawyer].first_name} 
                         ${data['lawyer_counter'][lawyer].surname}</b> : ${data['lawyer_counter'][lawyer].count}</p>`)
    }
    else{
        lawyer_service.append("<p>Адвокати не надавали послуги за заданий проміжок</p>")
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