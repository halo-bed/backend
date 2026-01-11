let sts = "OFF"
let last_events = []
let last_motion = null
let motion = null

const pubnub = new PubNub({
  publishKey: "pub-c-fc8a9a66-068b-49fe-a1e4-8f9ead36fcbc",
  subscribeKey: "sub-c-45f16351-7346-47d8-84d0-080414c6813c",
  userId: "web-user-" + Math.floor(Math.random() * 1000)
});

async function publishMessage(message) {
  try {
    const result = await pubnub.publish({
      message: message,
      channel: 'pir-control'
    });
    console.log("Message published with timetoken:", result.timetoken);
  } catch (error) {
    console.error("Publish failed:", error);
  }
}

pubnub.subscribe({
  channels: ["pir-events"]
});

function setLightUI(state) {
  const btnOn = document.getElementById("btn-on");
  const btnOff = document.getElementById("btn-off");
  if (!btnOn || !btnOff) return;

  btnOn.classList.remove("on-active");
  btnOff.classList.remove("off-active");

  if (state === "ON") btnOn.classList.add("on-active");
  else btnOff.classList.add("off-active");
}

function setMotionUI(state) {
  const motionText = document.getElementById("motion-text");
  if (!motionText) return;

  motionText.classList.remove("motion-detected", "motion-none", "muted");

  if (state === "ON") {
    motionText.textContent = "DETECTED";
    motionText.classList.add("motion-detected");
  } else {
    motionText.textContent = "NO MOTION";
    motionText.classList.add("motion-none");
  }
}

function setLastMotionUI(text) {
  const el = document.getElementById("last-motion-time");
  if (!el) return;
  el.textContent = text ? text : "--:--:--";
}

function setAutoOffUI(seconds) {
  const el = document.getElementById("autooff-seconds");
  if (!el) return;
  el.textContent = (seconds != null) ? `${seconds}s` : "--s";
}

pubnub.addListener({
  message: async function (event) {
    console.log("Raw PubNub event:", event);

    const msg = event.message;

    sts = msg.state;
    console.log("Updated status to:", sts);

    setLightUI(sts);
    setMotionUI(sts);

    if (sts === "ON") {
      await addEvent("Motion Detected");

      const now = new Date();
      const time = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      setLastMotionUI(time);
    }

    motion = sts === "ON" ? "Motion Detected" : "No Motion";
    console.log("Updated motion to:", motion);

    if (msg.autooff_seconds != null) {
      setAutoOffUI(msg.autooff_seconds);
    }
  },

  status: function (statusEvent) {
    if (statusEvent.category === "PNConnectedCategory") {
      console.log("Connected to PubNub channel");
    }
  }
});
