
$(document).ready(function(){
    var scroll = $(document).scrollTop();
    $(window).on('scroll',function(){
        if($(document).scrollTop() > scroll && $(document).scrollTop() > 100)
            $("#nav").fadeOut("fast");
        else {
            $("#nav").fadeIn("fast");
        }
        scroll = $(document).scrollTop();
    })
})
