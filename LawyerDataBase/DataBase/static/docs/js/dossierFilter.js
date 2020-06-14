$(document).ready(main());

function main() {
    var today  = Date.now()

    $('#date_signed_from_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change',setSignedTo);

    $('#date_signed_to_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change',setSignedFrom);

    $('#date_closed_from_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change',setClosedTo);

    $('#date_closed_to_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change',setClosedFrom);

    $('#date_expired_from_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change',setExpiredTo);

    $('#date_expired_to_search').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        disableTextInput: true,
    }).on('change',setExpiredFrom);
}

function setSignedTo() {
    var signedFrom = $('#date_signed_from_search').datepicker('getDate');
    $('#date_signed_to_search').datepicker('option','minDate', signedFrom)
}
function setClosedTo() {
    var closedFrom = $('#date_closed_from_search').datepicker('getDate');
    $('#date_closed_to_search').datepicker('option','minDate', closedFrom)
}
function setExpiredTo() {
    var expiredFrom = $('#date_expired_from_search').datepicker('getDate');
    $('#date_expired_to_search').datepicker('option','minDate', expiredFrom)
}

function setSignedFrom() {
    var signedTo = $('#date_signed_to_search').datepicker('getDate');
    $('#date_signed_from_search').datepicker('option','maxDate', signedTo)
}
function setClosedFrom() {
    var closedTo = $('#date_closed_to_search').datepicker('getDate');
    $('#date_closed_from_search').datepicker('option','maxDate', closedTo)
}
function setExpiredFrom() {
    var expiredTo = $('#date_expired_to_search').datepicker('getDate');
    $('#date_expired_from_search').datepicker('option','maxDate', expiredTo)
}
