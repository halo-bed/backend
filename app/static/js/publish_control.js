// slider_time = document.getElementById("auto-off-range");
// slider_time.addEventListener("input", () => {
//     message = {
//         "auto-off" : parseInt(slider_time.value)
//     }
//     publishMessage(message);
// })

// slider_brightness = document.getElementById("brightness-range");
// slider_brightness.addEventListener("input", () => {
//     message = {
//         "brightness" : parseInt(slider_brightness.value)
//     }
//     publishMessage(message);
// })

document.getElementById("save-time-window-btn").addEventListener("click", () => {
    start_time = document.getElementById("start-time").value;
    end_time = document.getElementById("end-time").value;

    message = {
        "start-time" : start_time,
        "end-time" : end_time
    }
    publishMessage(message);
    console.log("Published schedule:", message);
})