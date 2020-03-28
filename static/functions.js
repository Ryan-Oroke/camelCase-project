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

// function initMap()
// {
//     //Add a higher order function/"promises"
//     // The location of Uluru
//     //getLocation();
//     //var uluru = { lat: latVar, lng: lonVar };
//     var uluru = { lat: 40.050367699999995, lng: -105.24975579999999 };
//     // The map, centered at Uluru
//     //alert(latVar);
//     var map = new google.maps.Map(
//         document.getElementById('map'), { zoom: 14, center: uluru });
//     // The marker, positioned at Uluru
//     var marker = new google.maps.Marker({ position: uluru, map: map });
// }

//For more information or much of this code, see: https://developers.google.com/maps/documentation/javascript/geolocation
var map, infoWindow;

function initMap()
{
  map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 40.000, lng: -105 },
    zoom: 14,
    styles: [
      { elementType: 'geometry', stylers: [{ color: '#252525' }] },
      { elementType: 'labels.text.stroke', stylers: [{ color: '#242f3e' }] },
      { elementType: 'labels.text.fill', stylers: [{ color: '#746855' }] },
      {
        featureType: 'administrative.locality',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#d59563' }]
      },
      // {
      //   featureType: 'poi',
      //   elementType: 'labels.text.fill',
      //   stylers: [{color: '#d59563'}]
      // },
      {
        featureType: 'poi.park',
        elementType: 'geometry',
        stylers: [{ color: '#0d261a' }]
      },
      // {
      //   featureType: 'poi.park',
      //   elementType: 'labels.text.fill',
      //   stylers: [{color: '#6b9a76'}]
      // },
      {
        featureType: 'road',
        elementType: 'geometry',
        stylers: [{ color: '#404040' }]
      },
      {
        featureType: 'road',
        elementType: 'geometry.stroke',
        stylers: [{ color: '#212a37' }]
      },
      {
        featureType: 'road',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#9ca5b3' }]
      },
      {
        featureType: 'road.highway',
        elementType: 'geometry',
        stylers: [{ color: '#505050' }]
      },
      {
        featureType: 'road.highway',
        elementType: 'geometry.stroke',
        stylers: [{ color: '#1f2835' }]
      },
      {
        featureType: 'road.highway',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#f3d19c' }]
      },
      {
        featureType: 'transit',
        elementType: 'geometry',
        stylers: [{ color: '#2f3948' }]
      },
      {
        featureType: 'transit.station',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#d59563' }]
      },
      {
        featureType: 'water',
        elementType: 'geometry',
        stylers: [{ color: '#17263c' }]
      },
      {
        featureType: 'water',
        elementType: 'labels.text.fill',
        stylers: [{ color: '#515c6d' }]
      },
      {
        featureType: 'water',
        elementType: 'labels.text.stroke',
        stylers: [{ color: '#17263c' }]
      }
    ]
  });

  infoWindow = new google.maps.InfoWindow;

  if (navigator.geolocation)
  {
    navigator.geolocation.getCurrentPosition(function (position)
    {
      var pos = { lat: position.coords.latitude, lng: position.coords.longitude };

      infoWindow.setPosition(pos);
      infoWindow.setContent('Location Found');
      infoWindow.open(map);
      map.setCenter(pos);
    }, function ()
    {
      handleLocationError(true, infoWindow, map.getCenter());
    });
  } else
  {
    //Browser does not support geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

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
