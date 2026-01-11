from flask import Blueprint, request, session
from ..user.model import User
from ..events.model import Event
from ..extensions import mongo

events_bp = Blueprint('events', __name__)

@events_bp.route('/save_event', methods=['POST'])
def save_event():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401

    user_id = session['user_id']
    description = request.json.get('description')

    if not description:
        return {"error": "Description is required"}, 400

    event = Event(description=description, user_id=user_id)
    event_id = event.save()

    return {"message": "Event saved", "event_id": str(event_id)}, 201

@events_bp.route('/last_events', methods=['GET'])
def last_events():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401

    user_id = session['user_id']
    auth_provider = session.get("auth_provider", "default")
    result = Event.get_last_events_by_user(auth_provider, user_id, limit=5)

    return {"events": result}, 200