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