$(document).ready(function(){
    $(".articleaddtag").click(function(){
        article=$(".articleid").val();
        tag=$(this).val();
        $.post("/addarticletag/",{articleid:article,tagid:tag},function(result){
        });
    });
});

$(document).ready(function(){
	$("#textarea").keyup(function(){
		txt=$("#textarea").val();
		$.post("/markdown/",{suggest:txt},function(result){
			$("#markdown").html(result);
		});
	});
});
