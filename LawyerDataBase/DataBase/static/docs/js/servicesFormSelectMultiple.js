$(document).ready(main());

function main(){
    today = Date.now()
    $("#id_lawyers").selectpicker({
                title: "Оберіть Адвокатів",
                width: '395px',
                selectedTextFormat: 'count',
                liveSearch: true,
                liveSearchPlaceholder: "Пошук по адвокатам...",
                size: 6,
                noneResultsText: 'Не знайдено варіантів {0}',
                noneSelectedText : 'Нічого не обрано',
                countSelectedText: function (a,amount) {
                    if (a>4)
                        return `Обрано ${a} варіантів`
                    if (a===1)
                        return `Обрано ${a} варіант`
                    if (a>1)
                        return `Обрано ${a} варіанти`

                }
            })
    $('.bootstrap-select').css("margin-bottom", "25px");
    service = $('#id_service_code').val()
    $.ajax({
                type: "POST",
                async: true,
                url: '/database/lawyerServiceCode/',
                data: {
                    csrfmiddlewaretoken: getCookie('csrftoken'),
                    service: service,
                },
                success: setLawyers,
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log(textStatus, errorThrown);
                }
            });

}

function setLawyers(data){
    $("#id_lawyers").selectpicker('val', data['lawyers'])
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}