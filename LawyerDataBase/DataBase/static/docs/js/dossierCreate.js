$(document).ready(main());

function main() {
    var today  = Date.now()
    $('#id_date_closed').datepicker({
            dateFormat: "dd/mm/yy",
            changeMonth: true,
            changeYear: true,
            defaultDate: today,
        disableTextInput: true,
        })

    var date_signed = $('#id_date_signed')
    date_signed.datepicker({
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        minDate:today,
        disableTextInput: true,
    }).on('change',setDateSigned);

    $('#id_date_expired').datepicker({
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        changeYear: true,
        minDate:today,
        defaultDate: today,
        disableTextInput: true,
    })
}

function setDateSigned(event){
    var date_signed = $('#id_date_signed').datepicker('getDate');
    $('#id_date_expired').datepicker('option','minDate',date_signed + 7)
    $('#id_date_closed').datepicker('option','minDate',date_signed)
}