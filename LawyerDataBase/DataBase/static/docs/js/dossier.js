$(document).ready(main());


function main(){
    today = Date.now()
    $('#id_court_date').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        minDate:today,
        disableTextInput: true,
    })
    $('#id_date_closed').datepicker({
            dateFormat: "yy-mm-dd",
            changeMonth: true,
            changeYear: true,
            defaultDate: today,
        disableTextInput: true,
        })
}