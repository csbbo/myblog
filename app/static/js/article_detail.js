$("#comment_now").click(function(){
    var comment = $("#comment_content").val();
    var articleid = "{{article.id}}";
    if(comment.length==0){
        alert("评论内容为空");
    }
    else
    {
        $.post("/comment",{
            comment:comment,
            article_id:articleid
        },
        function(data,status){
            location.reload();//页面重载，似乎是在当前位置
            // alert("数据: \n" + JSON.parse(data).status + "\n状态: " + status);
        });
    }
});
