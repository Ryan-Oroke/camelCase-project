// function distanceSlid(name){
//     var dist = document.getElementById("modalHead").value;
//     document.getElementById("modalHead").innerHTML = "<h5>" + dist + " Feet </h5>";
// }

function openModal(){
    var distInput = document.getElementById("visibleDistanceSlider");
    var distText = document.getElementById("uploadDistLabel");
    var timeInput = document.getElementById("visibleTimeSlider");
    var timeText = document.getElementById("uploadTimeLabel");

    nameInput.onkeyup = function(){
        console.log("Done");
    }

    distInput.onclick = function(){
        var dist = distInput.value;
        distText.innerHTML =  dist + " Feet";
    }

    timeInput.onclick = function(){
        var time = timeInput.value;
        timeText.innerHTML = time + "Days";
    }
}