function geoFindMe(cb) {
    var output = document.getElementById("out");
    navigator.geolocation.getCurrentPosition(success, error);

    if (!navigator.geolocation) {
        output.innerHTML = "<p>Geolocation is not supported</p>";
        return {lat: 47.381723400000006, lon: 8.531773399999999};
    }


    function success(position) {
        // fire the call back!
        //console.log(position.coords.latitude, position.coords.longitude);
        cb(position.coords.latitude, position.coords.longitude);
    };


    function error() {
        output.innerHTML = "Unable to retrieve your location";
        return {lat: 47.381723400000006, lon: 8.531773399999999}
    };

    //output.innerHTML = "<p>Locating…</p>";
}