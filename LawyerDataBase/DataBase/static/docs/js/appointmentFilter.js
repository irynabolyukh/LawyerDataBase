$(document).ready(main());

function main() {
    var today = Date.now()
    $('#date_app_from_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change', setAppTo);

    $('#date_app_to_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change', setAppFrom);

    $('#time_app_from_search').timepicker({
        timeFormat: 'H:i',
        minTime: '10:00',
        maxTime: '19:00',
        interval: 15,
        disableTextInput: true,
    }).on('change',setTimeTo);
    $('#time_app_to_search').timepicker({
        timeFormat: 'H:i',
        minTime: '10:00',
        maxTime: '19:00',
        interval: 15,
        disableTextInput: true,
    }).on('change',setTimeFrom);
    $("#services_search").selectpicker({
                title: "Оберіть послугу",
                width: '395px',
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


function setTimeFrom() {
    var timeTo = $('#time_app_to_search').timepicker('getTime');
    $('#time_app_from_search').timepicker('option', 'maxTime', timeTo)
}

function setTimeTo() {
    var timeFrom = $('#time_app_from_search').timepicker('getTime');
    $('#time_app_to_search').timepicker('option', 'minTime', timeFrom)
}

function setAppFrom() {
    var appTo = $('#date_app_to_search').datepicker('getDate');
    $('#date_app_from_search').datepicker('option', 'maxDate', appTo)
}

function setAppTo() {
    var appFrom = $('#date_app_from_search').datepicker('getDate');
    $('#date_app_to_search').datepicker('option', 'minDate', appFrom)
}