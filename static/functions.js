function setCookie(cname, cvalue, exdays) {
	var d = new Date();
	d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
	var expires = "expires="+d.toUTCString();
	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
	var name = cname + "=";
	var ca = document.cookie.split(';');
	for(var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
			}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
			}
	}
	return "";
}

function login_request() {
   	var usrn=document.getElementById("usrn");
   	var pwd=document.getElementById("pwd");
   	var strArr=["username=", usrn, "&pwd=", pwd];
   	var str=strArr.join();
    var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
		document.getElementById("login_part").innerHTML = "Hi, ".concat(usrn);
		setCookie("username", usrn, 10);//Defalut of 10 day pass of cookie
		}
	};
	xhttp.open("POST", "some_url", true);
	//xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send(str);
}

function cookie_handle() {
	var user = getCookie("username");
	if (user != "") {
		document.getElementById("login_part").innerHTML="Hi, ".concat(usrn);
	} else{
		document.getElementById("login_part").innerHTML='<button class="btn btn-dark my-2 my-sm-0" type="button" onclick="location.href='.concat("'register.html'", ';">Register</button>&thinsp;<b>/</b>&thinsp;<form class="form-inline" action="login_request()"><input class="form-control mr-sm-2" type="text" placeholder="Username" aria-label="Username" id="usrn"><input class="form-control mr-sm-2" type="password" placeholder="Password" aria-label="Password" id="pwd"><button class="btn btn-dark my-2 my-sm-0" type="login">Sign In</button></form>&thinsp;<button class="btn btn-dark my-2 my-sm-0" type="button" onclick="location.href=', "'forget_password.html'", ';">Forget Password</button>');
	}
}

function validate_pass(){
    var lowerCaseLetters = /(?=.*[a-z])/g;
    var upperCaseLetters = /(?=.*[A-Z])/g;
    var numbers = /(?=.*\d)/g;
    var minLength = 8;
	var error_lower=false;
	var error_upper=false;
	var error_digit=false;
	var error_min_length=false;
	var error_match=false;
	if (document.getElementById("thePass1").value.match(lowerCaseLetters)) {
		error_lower=true;
		document.getElementById("lower").innerHTML="";
	}else{
		document.getElementById("lower").innerHTML="At least one lower case letter required. ";
	}
	if (document.getElementById("thePass1").value.match(upperCaseLetters)) {
		error_upper=true;
		document.getElementById("upper").innerHTML="";
	}else{
		document.getElementById("upper").innerHTML="At least one upper case letter required. ";
	}

	if (document.getElementById("thePass1").value.match(numbers)) {
	error_digit=true;
		document.getElementById("digit").innerHTML="";
	}else{
		document.getElementById("digit").innerHTML="At least one digit required. ";
	}
	if (document.getElementById("thePass1").value.length >= minLength) {
		error_min_length=true;
		document.getElementById("minlength").innerHTML="";
	}else{
		document.getElementById("minlength").innerHTML="Password should be at least 8 characters. ";
	}
	if (document.getElementById("thePass1").value == document.getElementById("thePass2").value) {
		error_match=true;
		document.getElementById("match").innerHTML="";
	}else{
		document.getElementById("match").innerHTML="Two passwords are not the same. ";
	}
	if (error_match && error_digit && error_upper && error_lower && error_min_length) {
		return true;
	}else{
		$("#modal_for_pass_error").modal();
		return false;
	}
}
