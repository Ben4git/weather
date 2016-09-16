function geoFindMe(cb) {
    var output = document.getElementById("out");
    navigator.geolocation.getCurrentPosition(success, error);

    if (!navigator.geolocation) {
        output.innerHTML = "<p>Geolocation is not supported by your browser</p>";
        return;
    }



    function success(position) {
        // fire the call back!
        cb(position.coords.latitude, position.coords.longitude);

        // show the map
        showMap(position.coords.latitude, position.coords.longitude);
    };

    function showMap(lat, lon) {
        var img = new Image();
        //output.innerHTML = '<p>Latitude is ' + lat + '° <br>Longitude is ' + lon + '°</p>';
        img.src = "http://maps.googleapis.com/maps/api/staticmap?center=" + lat + "," + lon + "&zoom=13&size=280x280&sensor=false";
        output.appendChild(img);
    }

    function error() {
        output.innerHTML = "Unable to retrieve your location";
        return {lat: 1, lon: 1}
    };

    //output.innerHTML = "<p>Locating…</p>";
}