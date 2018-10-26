//$(function () {

var selectedRange = 3;
var data;
var href;

var t = {
    label: "temperature",
    data: [],
    yaxis: 1
};

var h = {
    label: "humidity",
    data: [],
    yaxis: 2
};

var styleTemp = {
    size: 11,
    lineHeight: 13,
    style: "italic",
    weight: "bold",
    family: "sans-serif",
    variant: "small-caps",
    color: "#ffa500"
};

var styleHum = {
    size: 11,
    lineHeight: 13,
    style: "italic",
    weight: "bold",
    family: "sans-serif",
    variant: "small-caps",
    color: "#5ab8ff"
};

var options = {
    xaxis: {
        mode: "time",
        timeformat: "%a %H:%M",
        ticks: 5,
    },
    yaxes: [ {color:"#ffa500", min:10, max:50, font:styleTemp, tickSize:5}, { position: "right", min: 40, max:80, color:"#5ab8ff", font:styleHum, tickSize:10} ]
};

function writeTable(tMax, tMin, hMax, hMin) {
    $("#tNow").html(data['tempNOW']);
    $("#hNow").html(data['humNOW']);
    if (data['tempNOW'] < 20 || data['tempNOW'] > 40)
        $("#tNow").addClass("danger");
    else
        $("#tNow").removeClass("danger");
        
    if (data['humNOW'] < 50 || data['humNOW'] > 80)
        $("#hNow").addClass("danger");
    else
        $("#hNow").removeClass("danger");
    
    $("#tMax").html(tMax);
    $("#hMax").html(hMax);
    $("#tMin").html(tMin);
    $("#hMin").html(hMin);
}

function plot() {
    switch(selectedRange) {
        case 1:
            t['data'] = data['temp1'];
            h['data'] = data['hum1'];
            $.plot($("#plot"), [t, h], options);
            writeTable(data['temp1MAX'], data['temp1MIN'], data['hum1MAX'], data['hum1MIN']);
            break;
        case 3:
            t['data'] = data['temp3'];
            h['data'] = data['hum3'];
            $.plot($("#plot"), [t, h], options);
            writeTable(data['temp3MAX'], data['temp3MIN'], data['hum3MAX'], data['hum3MIN']);
            break;
        case 7:
            t['data'] = data['temp7'];
            h['data'] = data['hum7'];
            $.plot($("#plot"), [t, h], options);
            writeTable(data['temp7MAX'], data['temp7MIN'], data['hum7MAX'], data['hum7MIN']);
            break;
        default:
            break;
    }
}

function plot1() {
    selectedRange = 1;
    plot();
}

function plot3() {
    selectedRange = 3;
    plot();
}

function plot7() {
    selectedRange = 7;
    plot();
}

$.getJSON('tempHumData.json', function(d) {
    
    data = d;
    
    plot();
});

$("#modalForm").submit(function(e){
    $("#pinModal").modal('hide');
    $.ajax({
		type: "POST",
        url: "login",
		data: $("#modalForm").serialize(),
        success: function(data){
            if(data == "fail"){
				alert("Falsches Passwort!");
			}
            else {
                if (href !== "")
                    window.location.replace($SCRIPT_ROOT + href);
                else
                    location.reload();
            }
        }
    });
    $("#pinInputField").val("");
	e.preventDefault();
});

function login(link) {
    href = link;
    $("#pinModal").modal("show");
};

function logout() {
    $.ajax({
        type: "POST",
        url: "logout",
    });
    location.reload();
};
//});