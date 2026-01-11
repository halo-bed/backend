async function fetchEvents() {
    url = "http://127.0.0.1:5001/events/last_events"  // TODO: change after deploy
    response = await fetch(url)

    if (response.ok) {
        data = await response.json()
        return data.events
    } else {
        console.error("Failed to fetch events:", response.status, response.statusText)
    }
}

async function addEvent(msg) {
    url = "http://127.0.0.1:5001/events/save_event"

    response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "description": msg
        })
    })
}

document.getElementById("load-events-btn").addEventListener("click", fetchEvents);