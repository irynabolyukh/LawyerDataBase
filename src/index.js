import './scss/main.css';
import 'bootstrap'
import $ from 'jquery';

// console.log('auf');


$(document).ready(main());


function main() {
    gettotal()
}

function gettotal() {
    var nominal = $('#income_nom')[0].innerHTML.split(' ')[1];
    var bonus = $('#income_bonus')[0].innerHTML.split(' ')[1];
    console.log(nominal);
    console.log(bonus);
    var total = parseInt(bonus) + parseInt(nominal);
    $('#income_total')[0].innerHTML = total

}

