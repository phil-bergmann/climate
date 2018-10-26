var sl = $( "#slider" ).slider({
    animate: "fast",
    slide: function( event, ui ) {
        $("#sliderVal")[0].value = ui.value+"%";
        $('[name="intensity"]')[0].value = ui.value;
    },
    stop: function(event, ui) {
        console.log(ui.value);
    }
});

$.getJSON('admin/config.json', function(data) {
    sl.slider("value", data["intensity"]);
    $('[name="intensity"]')[0].value = sl.slider("value");
    $("#sliderVal")[0].value = sl.slider("value") + "%";
    $("#light_on")[0].value = data["light_on"];
    $("#light_off")[0].value = data["light_off"];
});