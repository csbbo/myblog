$(document).ready(function(){
	$("#textarea").keyup(function(){
		txt=$("#textarea").val();
		$.post("/markdown/",{suggest:txt},function(result){
			$("#markdown").html(result);
		});
	});
});
