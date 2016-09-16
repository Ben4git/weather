var $button = jQuery("#btnTest");
    $button.on("click", onBtnClick);

    function onBtnClick() {
        console.log("button clicked");
        geoData();
    }

    function geoData() {
        //new Vue({
        //    el: '#geolocation',
        //    data: {
        //    lat: geoloca.lat,
        //    lon: geoloca.lon
        //    }
        //})

        $.ajax({
                 url: "http://localhost:5000/geolLoca/"+geoloca.lat+"/"+geoloca.lon+"/",
                 success: onSuccess,
                 dataType: "json"
        });
    }

    function onSuccess(geoloca) {
        console.log("success", geoloca);
        geoloca.lat
        geoloca.lon

         jQuery(".app").html( "lat:" + geoloca.lat + "lon: " + geoloca.lon );
    }

    function onError(err) {
        console.log("error", err);
    }
