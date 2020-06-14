$(document).ready(main());
var dayNames = ['Понеділок',"Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]
var dayNamesShort = ['Пн',"Вт","Ср","Чт","Пт","Сб","Нд"]
var MonthNames = ["Січень","Лютий","Березень","Квітень","Травень",
    "Червень","Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"]
var monthNamesShort = ['Січ',"Лют","Бер","Квіт","Трав",
    "Чер","Лип","Сер","Вер","Жов","Лист","Груд"]

function main(){
    today = Date.now()
    $('#id_court_date').datepicker({
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
    })
    $('#id_date_closed').datepicker({
            dateFormat: "yy-mm-dd",
            changeMonth: true,
            changeYear: true,
            defaultDate: today,
        disableTextInput: true,
        dayNames: dayNames,
        dayNamesMin: dayNamesShort,
        monthNames : MonthNames,
        monthNamesShort:monthNamesShort,
        })
}