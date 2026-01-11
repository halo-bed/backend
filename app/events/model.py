from ..extensions import mongo
from datetime import datetime
from bson import ObjectId

class Event:
    def __init__(
        self,
        description,
        timestamp=None,
        id=None,
        user_id=None
    ) :
        self.description = description
        self.timestamp = datetime.now() if timestamp is None else timestamp
        self.id = id
        self.user_id = ObjectId(user_id) if user_id else None

    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "description": self.description,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_dict(data):
        return Event(
            description=data.get("description"),
            timestamp=data.get("timestamp"),
            id=data.get("_id"),
            user_id=data.get("user_id")
        )
    
    @staticmethod
    def get_last_events_by_user(auth_provider, user_id, limit=5):
        events_cursor = mongo.db.events.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        return [Event.from_dict(event_data).to_dict() for event_data in events_cursor]

    def save(self):
        event_data = self.to_dict()
        result = mongo.db.events.insert_one(event_data)
        self.id = result.inserted_id
        return self.id
        