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

pubnub.addListener({
    message: async function (event) {
        console.log("Raw PubNub event:", event);

        const msg = event.message;

        sts = msg.state;
        console.log("Updated status to:", sts);

        if (sts === "ON") {
            await addEvent("Motion Detected");
            console.log("Added 'Motion Detected' event");

            last_events = await fetchEvents();
            console.log("Fetched last events:", last_events);

            last_motion = last_events.length > 0 ? last_events[last_events.length - 1].timestamp.$date : null;
            console.log("Updated last motion to:", last_motion);

        }

        motion = sts === "ON" ? "Motion Detected" : "No Motion";
        console.log("Updated motion to:", motion);
    },

    status: function (statusEvent) {
        if (statusEvent.category === "PNConnectedCategory") {
            console.log("Connected to PubNub channel");
        }
    }
});
