$(document).ready(main());

var dayNames = ['Понеділок',"Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]
var dayNamesShort = ['Пн',"Вт","Ср","Чт","Пт","Сб","Нд"]
var MonthNames = ["Січень","Лютий","Березень","Квітень","Травень",
    "Червень","Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"]
var monthNamesShort = ['Січ',"Лют","Бер","Квіт","Трав",
    "Чер","Лип","Сер","Вер","Жов","Лист","Груд"]
function main() {
    var today  = Date.now()

    var date_signed = $('#id_date_signed')
    date_signed.datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        defaultDate: today,
        minDate:today,
        disableTextInput: true,
        dayNames: dayNames,
        dayNamesMin: dayNamesShort,
        monthNames : MonthNames,
        monthNamesShort:monthNamesShort,
    }).on('change',setDateSigned);

    $('#id_date_expired').datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        minDate:today,
        defaultDate: today,
        disableTextInput: true,
        dayNames: dayNames,
        dayNamesMin: dayNamesShort,
        monthNames : MonthNames,
        monthNamesShort:monthNamesShort,
    })
}

function setDateSigned(event){
    var date_signed = $('#id_date_signed').datepicker('getDate');
    var date_expired = new Date(date_signed.getFullYear(),
             date_signed.getMonth(),
             date_signed.getDate() + 7)
    $('#id_date_expired').datepicker('option','minDate', date_expired)
    $('#id_date_closed').datepicker('option','minDate', date_signed)
}