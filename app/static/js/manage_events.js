async function fetchEvents() {
  const response = await fetch("http://127.0.0.1:5001/events/last_events");  // TODO: change after deploy

  if (response.ok) {
    const data = await response.json();
    return data.events;
  } else {
    console.error("Failed to fetch events:", response.status);
    return [];
  }
}

async function addEvent(msg) {
  await fetch("http://127.0.0.1:5001/events/save_event", { 
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description: msg })
  });
}

function formatEventTime(timestamp) {
  if (!timestamp) return "--:--:--";

  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return "--:--:--";

  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function renderEvents(events) {
  const list = document.getElementById("events-list");
  if (!list) return;

  if (!events || events.length === 0) {
    list.innerHTML = `<div class="muted">No events yet</div>`;
    return;
  }

  list.innerHTML = "";

  events.forEach(ev => {
    const time = formatEventTime(ev.timestamp.$date);
    const text = ev.description || "Event";

    const item = document.createElement("div");
    item.className = "event-item";

    item.innerHTML = `
      <img class="event-icon" src="/static/scss/clock.png" alt="clock">
      <div class="event-time">${time}</div>
      <div class="event-text">${text}</div>
    `;

    list.appendChild(item);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const events = await fetchEvents();
  renderEvents(events);
});

async function refreshEventsUI() {
  const events = await fetchEvents();
  renderEvents(events);
}
