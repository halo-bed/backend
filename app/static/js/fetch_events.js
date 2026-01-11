async function fetchEvents() {
    url = "http://127.0.0.1:5000/events/last_events"  // TODO: change after deploy
    response = await fetch(url)

    if (response.ok) {
        data = await response.json()
        console.log(data)
    } else {
        console.error("Failed to fetch events:", response.status, response.statusText)
    }
}

document.getElementById("load-events-btn").addEventListener("click", fetchEvents);