$(document).ready(main());

function main() {
    var d = new Date().toLocaleString();
    document.getElementById("date").innerHTML = d;
}