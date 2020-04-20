var latVar = -50, lonVar = 0.0;

function getLocation()
{

    var position = navigator.geolocation.getCurrentPosition(coords.longitude);
    alert(position);
    if (navigator.geolocation)
    {
        document.getElementById("gps_lat_form").value = position.coords.latitude;
        document.getElementById("gps_long_form").value = position.coords.longitude;
        var latlon = position.coords.latitude + "," + position.coords.longitude;
        latVar = position.coords.latitude;
        lonVar = position.coords.longitude;
        alert(latlon);
    } else
    {
        alert("Could not get location!");
    }
}

function setPosition(position)
{


}
