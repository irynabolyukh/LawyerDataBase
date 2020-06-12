$(document).ready(main());


function main(){
    $('#id_court_date').datepicker({
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        changeYear: true,
        defaultDate: Date.now(),
        minDate:Date.now(),
        disableTextInput: true,
    })

}