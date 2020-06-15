$(document).ready(main());

function main(){
    today = Date.now()
    $("#id_service").selectpicker({
                title: "Оберіть послуги",
                width: '395px',
                selectedTextFormat: 'count',
                liveSearch: true,
                liveSearchPlaceholder: "Пошук по послугам...",
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
            });

    $("#id_work_days").selectpicker({
                title: "Оберіть дні роботи",
                width: '250px',
                selectedTextFormat: 'count',
                size: 7,
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
            });
}