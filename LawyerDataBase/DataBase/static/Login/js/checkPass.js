$("input[type='password']").on("input", function () {
    validate();
});
function validate(){
    var show = true;
    $("input[type='password']").each(function(){
        if($(this).val()!='hello'){
            show = false;
        }
    });
    if(show){
        $('#btn-submit').css({cursor:'pointer'})
        $('#btn-submit').removeAttr('disabled')
    }
    else {
        $('#btn-submit').css({cursor:'not-allowed'})
    }
};