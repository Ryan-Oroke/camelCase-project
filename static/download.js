var latVar = -50, lonVar = 0.0;

                function getLocation()
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

                function setPosition(position)
                {


                }

                function initMap()
                {
                    //Add a higher order function/"promises"
                    // The location of Uluru
                    //getLocation();
                    //var uluru = { lat: latVar, lng: lonVar };
                    var uluru = { lat: 40.050367699999995, lng: -105.24975579999999 };
                    // The map, centered at Uluru
                    //alert(latVar);
                    var map = new google.maps.Map(
                        document.getElementById('map'), { zoom: 14, center: uluru });
                    // The marker, positioned at Uluru
                    var marker = new google.maps.Marker({ position: uluru, map: map });
                }