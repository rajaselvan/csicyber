var map = new google.maps.Map(document.getElementById('map_canvas'), {
    zoom: 5,
    center: new google.maps.LatLng(35.137879, -82.836914),
    mapTypeId: google.maps.MapTypeId.ROADMAP
});

var myMarker = new google.maps.Marker({
    position: new google.maps.LatLng(47.651968, 9.478485),
    draggable: true
});

google.maps.event.addListener(myMarker, 'dragend', function (evt) {

    document.getElementById('lat').value = evt.latLng.lat().toFixed(6).toString();
    document.getElementById('long').value = evt.latLng.lng().toFixed(6).toString();
    map.setCenter(myMarker.position);

});



map.setCenter(myMarker.position);

myMarker.setMap(map);

$(document).ready(function () {
    $("#after_long").click(function () {
        var latitude = $("#lat").val();
        var longitude = $("#long").val();
        var latlng = new google.maps.LatLng(latitude, longitude);
        myMarker.setPosition(latlng);
        map.setCenter(myMarker.position);


    });


});

function loading() {

    $("#loading").show();
    $("#content").hide();
}

