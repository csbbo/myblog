function validateForm(){
    var password1,password2;
    password1 = document.getElementById("pwd1").value;
    password2 = document.getElementById("pwd2").value;
    if(password1==password2)
    {
        return true;
    }
    else{
        // 似乎出现异常会返回true
        document.getElementById("passwordwrone").style.display="block";
        return false;
    }
}
