$(document).ready(main());
var dayNames = ['Понеділок',"Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]
var dayNamesShort = ['Пн',"Вт","Ср","Чт","Пт","Сб","Нд"]
var MonthNames = ["Січень","Лютий","Березень","Квітень","Травень",
    "Червень","Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"]
var monthNamesShort = ['Січ',"Лют","Бер","Квіт","Трав",
    "Чер","Лип","Сер","Вер","Жов","Лист","Груд"]

function main(){
    $('#id_birth_date').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        maxDate: '-16y',
        disableTextInput: true,
        dayNames: dayNames,
        dayNamesMin: dayNamesShort,
        monthNames : MonthNames,
        monthNamesShort:monthNamesShort,
    }).on('change',setPassportDate);

    $('#id_passport_date').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        maxDate: "+0d",
        disableTextInput: true,
        dayNames: dayNames,
        dayNamesMin: dayNamesShort,
        monthNames : MonthNames,
        monthNamesShort:monthNamesShort,
    })
}

function setPassportDate(event){
    var birthdate = $('#id_birth_date').datepicker("getDate");
    var newDay = new Date(birthdate.getFullYear() +14, birthdate.getMonth(), birthdate.getDate())
     $('#id_passport_date').datepicker('option','minDate', newDay)
}