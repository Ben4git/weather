var getLocationData = geoFindMe(function (latitude, longitude) {
    //console.log("this is the callback", latitude, longitude);
    getGeoData(latitude, longitude);
    getWeather(latitude, longitude);
    predictWeather(latitude, longitude)
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
    });
}

function predictWeather(lat, lon) {
    $.ajax({
        method: "GET",
        url: "//localhost:5000/weatherPrediction/" + lat + "/" + lon + "/"
    })
    .done(function (prediction) {
        console.log("Data Prediction: ", prediction);
        new Vue({
            el: '#prediction',
            data: {
                loading: false,
                items: prediction
            }
        });
    });
}


