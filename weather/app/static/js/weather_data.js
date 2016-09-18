var getLocationData = geoFindMe(function (latitude, longitude) {
    //console.log("this is the callback", latitude, longitude);
    getGeoData(latitude, longitude);
    getWeather(latitude, longitude)
});

var loca = {
    lat: 0,
    lon: 0
};

function getGeoData(lat, lon) {
    $.ajax({
        method: "GET",
        url: "//localhost:5000/geoLoca/" + lat + "/" + lon + "/"
    })
        .done(function (res) {
            //console.log("Data Saved: ", res);
            new Vue({
                el: '#geo',
                data: {
                    loading: false,
                    items: res
                    }
            });
        });
}

function getWeather(lat, lon) {
    $.ajax({
        method: "GET",
        url: "//localhost:5000/weatherReport/" + lat + "/" + lon + "/"
    })
    .done(function (weather_json) {
        console.log("Data Weather: ", weather_json);
        new Vue({
            el: '#weather-table',
            data: {
                loading: false,
                items: weather_json
            }
        });
        predictWeather(weather_json)
    });
}

function predictWeather(weather_json) {
    $.ajax({
        method: "GET",
        url: "//localhost:5000/weatherPrediction/" + weather_json + "/"
    })
    .done(function (temperature) {
        console.log("Data Prediction: ", temperature);
        new Vue({
            el: '#prediction',
            data: {
                loading: false,
                items: temperature
            }
        });
    });
}


