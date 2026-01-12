let sts = "OFF";
let last_events = [];
let last_motion = null;
let motion = null;
let autoOffTimer = null;
let autoOffSeconds = null;

const pubnub = new PubNub({
  publishKey: "pub-c-fc8a9a66-068b-49fe-a1e4-8f9ead36fcbc",
  subscribeKey: "sub-c-45f16351-7346-47d8-84d0-080414c6813c",
  userId: "web-user-" + Math.floor(Math.random() * 1000)
});


async function fetchPubNubToken() {
  const res = await fetch("/auth/pubnub-token", {
    method: "GET",
    credentials: "include"
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to fetch PubNub token (${res.status}): ${text}`);
  }

  const data = await res.json();
  if (!data.token) throw new Error("Token response missing 'token' field");
  return data.token;
}

async function initPubNub() {
  try {
    const token = await fetchPubNubToken();
    pubnub.setToken(token);

    pubnub.addListener({
      message: async function (event) {
        console.log("Raw PubNub event:", event);

        const msg = event.message || {};

        let newState = msg.state;
        if (!newState && typeof msg.led === "string") {
          newState = msg.led.toUpperCase(); // "OFF"/"ON"
        }
        if (!newState) newState = "Unknown";

        sts = newState;
        console.log("Updated status to:", sts);

        setLightUI(sts);
        setMotionUI(sts);

        if (sts === "OFF" && autoOffTimer) {
          clearInterval(autoOffTimer);
          autoOffTimer = null;
          setAutoOffUI(0);
        }

        motion = null;
        switch (sts) {
          case "ON":
            motion = "Motion Detected: LED ON";
            break;
          case "OFF":
            motion = "No Motion: LED OFF";
            break;
          case "updated":
          case "UPDATED":
            motion = "Setting Updated";
            break;
          default:
            motion = "Unknown";
        }

        console.log("Updated motion to:", motion);

        if (typeof addEvent === "function") {
          await addEvent(`${motion}`);
        }

        if (typeof refreshEventsUI === "function") {
          refreshEventsUI();
        }

        const time = msg.ts
          ? new Date(Number(msg.ts) * 1000).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit"
            })
          : new Date().toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit"
            });

        setLastMotionUI(time);

        if (msg.auto_off != null) {
          startAutoOffCountdown(Number(msg.auto_off));
        }
      },

      status: function (statusEvent) {
        console.log("PubNub status:", statusEvent.category);

        if (statusEvent.category === "PNConnectedCategory") {
          console.log("Connected to PubNub channel");
        }
      }
    });

    pubnub.subscribe({
      channels: ["pir-events"]
    });

    console.log("Subscribed to pir-events with PAM token ✅");
  } catch (err) {
    console.error("PubNub init failed:", err);
  }
}


async function publishMessage(message) {
  try {
    const result = await pubnub.publish({
      message: message,
      channel: "pir-control"
    });
    console.log("Message published with timetoken:", result.timetoken);
  } catch (error) {
    console.error("Publish failed:", error);
  }
}

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
  const lastMotionElement = document.getElementById("last-motion-time");
  if (!lastMotionElement) return;

  lastMotionElement.textContent = text ? text : "--:--:--";
}

function setAutoOffUI(seconds) {
  const autoOffElement = document.getElementById("autooff-seconds");
  if (!autoOffElement) return;

  autoOffElement.textContent = seconds <= 0 ? "--s" : `${seconds}s`;
}

function startAutoOffCountdown(seconds) {
  autoOffSeconds = seconds;

  if (autoOffTimer) {
    clearInterval(autoOffTimer);
  }

  setAutoOffUI(autoOffSeconds);

  autoOffTimer = setInterval(() => {
    autoOffSeconds--;

    if (autoOffSeconds <= 0) {
      clearInterval(autoOffTimer);
      autoOffTimer = null;
      setAutoOffUI(0);
      return;
    }

    setAutoOffUI(autoOffSeconds);
  }, 1000);
}

// Kick it off
initPubNub();
