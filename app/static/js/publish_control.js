const slider_time = document.getElementById("auto-off-range");
const slider_brightness = document.getElementById("brightness-range");

const brightnessValue = document.getElementById("brightness-value");
const autooffValue = document.getElementById("autooff-setting-value");

function updateBrightnessText() {
  if (brightnessValue) brightnessValue.textContent = slider_brightness.value + "%";
}

function updateAutoOffText() {
  if (autooffValue) autooffValue.textContent = slider_time.value + "s";
}

if (slider_brightness) updateBrightnessText();
if (slider_time) updateAutoOffText();

if (slider_brightness) {
  slider_brightness.addEventListener("input", () => {
    updateBrightnessText();
  });
}

if (slider_time) {
  slider_time.addEventListener("input", () => {
    updateAutoOffText();
  });
}

const saveBtn = document.getElementById("save-settings-btn");
if (saveBtn) {
  saveBtn.addEventListener("click", () => {
    const message = {
      brightness: parseInt(slider_brightness.value),
      "auto-off": parseInt(slider_time.value)
    };

    publishMessage(message);
    console.log("Published settings:", message);
  });
}

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