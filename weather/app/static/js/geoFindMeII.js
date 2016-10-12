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
    };


    function error() {
        output.innerHTML = "Unable to retrieve your location";
        return {lat: 1, lon: 1}
    };

    //output.innerHTML = "<p>Locating…</p>";
}