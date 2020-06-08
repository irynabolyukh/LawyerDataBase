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
    $('#closed_dossier')[0].innerHTML = data['closed']
    $('#open_dossier_j')[0].innerHTML = data['open_j'];
    $('#open_dossier_n')[0].innerHTML = data['open_n'];
    $('#open_dossier')[0].innerHTML = data['open'];
    $('#total_value')[0].innerHTML = data['value'];






    var serviceContainer = $('#services_container')
    serviceContainer.empty()

    if (data['service_count'].length > 0) {
        serviceContainer.append(`<table class="table table-hover table_border" id="services">
                <thead class="thead-dark">
                    <tr>
                        <th>Назва</th>
                        <th>Номінальна вартість</th>
                        <th>Бонусна вартість</th>
                        <th>Кількість записів</th>
                        <th>Загальна сума</th>
                    </tr>

                </thead>
                <tbody id="services_body">`)
        var servicesBody = $('#services_body')
        for (var service of data['service_count']) {
            servicesBody.append(
                `<tr class="border_top">
                        <th rowspan="2" class="vertical_align">
                            <a href="/database/service/${service.service_code}/">${service.name_service}</a></th>
                        <th>${service.nominal_value}</th>
                        <th>${service.bonus_value}</th>
                        <th>${service.count}</th>
                        <th>${service.sum} грн</th>
                    </tr>
                    <tr>
                        <th></th>
                        <th class="lnr-text-align-right">За весь час</th>
                        <th>${service.fulltimeCount}</th>
                        <th>${service.fulltimeSum} грн</th>
                    </tr>`)
        }
        serviceContainer.append(` </tbody></table>`)
    }
    else{
        serviceContainer.append("<h6 >За заданий проміжок не були надані послуги</h6>")
    }

    var lawyerContainer = $('#lawyer_container')
    lawyerContainer.empty()

    if (data['lawyer_counter'].length > 0) {
        lawyerContainer.append(`<table class="table table-hover table_border" id="lawyers">
                <thead class="thead-dark">
                    <tr>
                        <th>ПІБ</th>
                        <th>Код адвоката</th>
                        <th>Спеціалізація</th>
                        <th>Кількість записів</th>
                        <th>Загальна сума</th>
                    </tr>
                </thead>
                <tbody id="lawyers_body">`)
        var lawyerBody = $('#lawyers_body')
        for (var lawyer of data['lawyer_counter']) {
            lawyerBody
                .append(
                    `<tr>
                        <th><a href="/database/lawyer/${lawyer.lawyer_code}">
                            ${lawyer.first_name} ${lawyer.surname} ${lawyer.mid_name}</a></th>
                        <th>${lawyer.lawyer_code}</th>
                        <th>${lawyer.spec}</th>
                        <th>${lawyer.count}</th>
                        <th>${lawyer.sum} грн</th>
                    </tr>
                    `)
        }
        lawyerContainer.append(` </tbody></table>`)
    }
    else{
        lawyerContainer.append("<h6 >За заданий проміжок адвокати не надавали послуги</h6>")
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