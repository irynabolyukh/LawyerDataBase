$(document).ready(main());

var lawyerWorkDays = []
var blockedTime = []

function main() {
    $('#id_app_time').timepicker({
        timeFormat: 'H:i',
        minTime: '10:00',
        maxTime: '19:00',
        interval: 15,
        disableTextInput: true,
        disableTimeRanges: blockedTime,
    }).on('change',checkTime);


    $('#id_app_date').attr('autocomplete',"off").datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        constrainInput: true,
        minDate: "+2d",
        maxDate: "+3m",
        beforeShowDay: blockdays
    });
    $('#id_service')[0].addEventListener('change', service_ajax_request);
    $('#id_lawyer_code')[0].addEventListener('change', lawyer_workdays_request);
    $('#id_app_date').on('change', time_blocked_request);
    try {
        $('#id_num_client_n')[0].addEventListener('change',dossier_ajax_request);

    }
    catch (e) {
        $('#id_num_client_j')[0].addEventListener('change',dossier_ajax_request);
    }

    if ($('#id_lawyer_code').val() !== ""){
        lawyer_workdays_request()
    }
     if ($('#id_app_date').val() !== ""){
        time_blocked_request()
    }

     $("#id_service").selectpicker({
                title: "Оберіть послугу",
                width: '395px',
                selectedTextFormat: 'count',
                liveSearch: true,
                liveSearchPlaceholder: "Пошук по послугам...",
                size: 6,
                noneResultsText: 'Не знайдено варіантів {0}',
                noneSelectedText : 'Нічого не обрано',
                countSelectedText: function (a,amount) {
                    if (a>4)
                        return `Обрано ${a} варіантів`
                    if (a===1)
                        return `Обрано ${a} варіант`
                    if (a>1)
                        return `Обрано ${a} варіанти`

                }
            });

}


function lawyer_workdays_request(event){
    var lawyer = $('#id_lawyer_code').val()

    var dossier =$('#id_code_dossier_n').val()
    var dosN = true;
    try {
        if (dossier.length === 0) {
            dossier = $('#id_code_dossier_j').val()
            dosN = false;
        }
    }
    catch (e){
        dossier = $('#id_code_dossier_j').val()
        dosN = false;
    }

    $('#id_app_time').timepicker({
        timeFormat: 'H:i',
        minTime: '10:00',
        maxTime: '19:00',
        interval: 15,
        disableTextInput: true,
        disableTimeRanges: blockedTime,
    }).on('change',checkTime);

    $.ajax({
                type: "POST",
                async: true,
                url: '/database/lawyerWorkDays/',
                data: {
                    csrfmiddlewaretoken: getCookie('csrftoken'),
                    lawyer: lawyer,
                    dossier: dossier,
                    dosn : dosN

                },
                success: setWorkDays,
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log(textStatus, errorThrown);
                }
            });
}

function time_blocked_request(event) {

    date2 = $('#id_app_date').datepicker("getDate");
    lawyer = $('#id_lawyer_code').val()
    $.ajax({
        type: "POST",
        async: true,
        url: '/database/dayBlockedTime/',
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            date: {
                day: date2.getDate(),
                month: String(parseInt(date2.getMonth()) + 1),
                year: date2.getFullYear(),
            },
            lawyer: lawyer,
        },
        success: setblockedTime,
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        }
    });
}


function setblockedTime(data){
    var timestamp = ''
    var plusHour = ''
    blockedTime = []
    for (item of data['time']){

        timestamp = item['time'].split(':');
        plusHour = '' + (parseInt(timestamp[0]) + item['count']);
        plusHour += ':' + ((parseInt(timestamp[1]) + 10)%60)

        //creating time pair
        var array = []
        array.push(item['time']);
        array.push(plusHour);

        blockedTime.push(array)
    }
    $('#id_app_time').timepicker({
        timeFormat: 'H:i',
        minTime: '10:00',
        maxTime: '19:00',
        interval: 15,
        disableTextInput: true,
        disableTimeRanges: blockedTime,
    }).on('change',checkTime);
}

function setWorkDays(data){
    lawyerWorkDays  = data['days'];
    try {
        var maxdateSplit = data['maxday']
        maxdateSplit = maxdateSplit.split('-')
        var maxDate = new Date(maxdateSplit[0], maxdateSplit[1]-1, maxdateSplit[2])
        $('#id_app_date').datepicker('option', 'maxDate', maxDate)
    }
    catch (e) {

    }
}

function blockdays(date){
    var datebool = lawyerWorkDays.indexOf(date.getUTCDay() + 1) !== -1
    return [datebool]
}

function checkTime(event){
    var time_element = $('#id_app_time');
    try{
        var selected_time = time_element.timepicker('getTime');
        // check if time is between 10 and 19
        if (selected_time.getHours() > 19 || selected_time.getHours() < 10){
            time_element.val("");
            time_element.addClass("wrong_input")
        }
        // time is right
        else {
            time_element.removeClass("wrong_input")
        }
    }
    catch (e) {
        time_element.val("");
        time_element.addClass("wrong_input")
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
                            ${data['lawyers'][item].first_name} ${data['lawyers'][item].surname}  ${data['lawyers'][item].mid_name}, ${data['lawyers'][item].spec}</option>`)
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