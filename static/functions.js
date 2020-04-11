var latVar = -50, lonVar = 0.0;

function getLocation(initMap)
{

  var position = navigator.geolocation.getCurrentPosition(coords.longitude);
  alert(position);
  if (navigator.geolocation)
  {
    var latlon = position.coords.latitude + "," + position.coords.longitude;
    alert(latlon);
  } else
  {
    alert("Could not get location!");
  }
}

// This code was moved into download.html
//For more information or much of this code, see: https://developers.google.com/maps/documentation/javascript/geolocation
var map, infoWindow;

//function initMap()
//{
//  map = new google.maps.Map(document.getElementById('map'), {
//    center: { lat: 40.000, lng: -105 },
//    zoom: 14,
//    styles: [
//      { elementType: 'geometry', stylers: [{ color: '#252525' }] },
//      { elementType: 'labels.text.stroke', stylers: [{ color: '#242f3e' }] },
//      { elementType: 'labels.text.fill', stylers: [{ color: '#746855' }] },
//      {
//        featureType: 'administrative.locality',
//        elementType: 'labels.text.fill',
//        stylers: [{ color: '#d59563' }]
//      },
//      // {
//      //   featureType: 'poi',
//      //   elementType: 'labels.text.fill',
//      //   stylers: [{color: '#d59563'}]
//      // },
//      {
//        featureType: 'poi.park',
//        elementType: 'geometry',
//        stylers: [{ color: '#0d261a' }]
//      },
//      // {
//      //   featureType: 'poi.park',
//      //   elementType: 'labels.text.fill',
//      //   stylers: [{color: '#6b9a76'}]
//      // },
//      {
//        featureType: 'road',
//        elementType: 'geometry',
//        stylers: [{ color: '#404040' }]
//      },
//      {
//        featureType: 'road',
//        elementType: 'geometry.stroke',
//        stylers: [{ color: '#212a37' }]
//      },
//      {
//        featureType: 'road',
//        elementType: 'labels.text.fill',
//        stylers: [{ color: '#9ca5b3' }]
//      },
//      {
//        featureType: 'road.highway',
//        elementType: 'geometry',
//        stylers: [{ color: '#505050' }]
//      },
//      {
//        featureType: 'road.highway',
//        elementType: 'geometry.stroke',
//        stylers: [{ color: '#1f2835' }]
//      },
//      {
//        featureType: 'road.highway',
//        elementType: 'labels.text.fill',
//        stylers: [{ color: '#f3d19c' }]
//      },
//      {
//        featureType: 'transit',
//        elementType: 'geometry',
//        stylers: [{ color: '#2f3948' }]
//      },
//      {
//        featureType: 'transit.station',
//        elementType: 'labels.text.fill',
//        stylers: [{ color: '#d59563' }]
//      },
//      {
//        featureType: 'water',
//        elementType: 'geometry',
//        stylers: [{ color: '#17263c' }]
//      },
//      {
//        featureType: 'water',
//        elementType: 'labels.text.fill',
//        stylers: [{ color: '#515c6d' }]
//      },
//      {
//        featureType: 'water',
//        elementType: 'labels.text.stroke',
//        stylers: [{ color: '#17263c' }]
//      }
//    ]
//  });
//
//  infoWindow = new google.maps.InfoWindow;
//
//  if (navigator.geolocation)
//  {
//    navigator.geolocation.getCurrentPosition(function (position)
//    {
//      var pos = { lat: position.coords.latitude, lng: position.coords.longitude };
//      var cirlcle = new google.maps.Circle({
//          map: map,
//          center: pos,
//          radius: 1000 //In meters
//      });
//      infoWindow.setPosition(pos);
//      infoWindow.setContent('Location Found');
//      infoWindow.open(map);
//      map.setCenter(pos);
//    }, function ()
//    {
//      handleLocationError(true, infoWindow, map.getCenter());
//    });
//  } else
//  {
//    //Browser does not support geolocation
//    handleLocationError(false, infoWindow, map.getCenter());
//  }
//}

function handleLocationError(browserHasGeolocation, infoWindow, pos)
{
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
    'Error: The Geolocation service failed' :
    'Error: Your browser doesn\'t support geolocation.');
  infoWindow.open(map);
}

function openUploadModal(){
  var distInput = document.getElementById("visibleDistanceSlider");
  var distText = document.getElementById("uploadDistLabel");
  var timeInput = document.getElementById("visibleTimeSlider");
  var timeText = document.getElementById("uploadTimeLabel");

  nameInput.onkeyup = function(){
      console.log("Done");
  }

  distInput.onclick = function(){
      var dist = distInput.value;
      distText.innerHTML =  dist + " Feet";
  }

  timeInput.onclick = function(){
      var time = timeInput.value;
      timeText.innerHTML = time + "Days";
  }
}

function openInspectModal(){

}
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
