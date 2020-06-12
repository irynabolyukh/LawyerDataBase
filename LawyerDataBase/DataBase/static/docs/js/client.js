$(document).ready(main());

function main(){
    $('#id_birth_date').datepicker({
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        changeYear: true,
        maxDate: '-16y',
        disableTextInput: true,
    }).on('change',setPassportDate);

    $('#id_passport_date').datepicker({
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        changeYear: true,
        maxDate: "+0d",
        disableTextInput: true,
    })
}

function setPassportDate(event){
    var birthdate = $('#id_birth_date').datepicker("getDate");
    var newDay = new Date(birthdate.getFullYear() +14, birthdate.getMonth(), birthdate.getDate())
     $('#id_passport_date').datepicker('option','minDate', newDay)
}