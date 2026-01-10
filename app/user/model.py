from app.extensions import mongo
import bson
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User:
    def __init__(
            self,
            device_id,
            username,
            password,
            email,
            created_at=None,
            id=None
    ):
        self.id = id
        self.device_id = str(device_id) if device_id else None
        self.username = username
        self.password = password
        self.email = email
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        doc = {
            "device_id": self.device_id,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "created_at": self.created_at
        }

        if self.id:
            doc["_id"] = bson.ObjectId(self.id) if not isinstance(self.id, bson.ObjectId) else self.id

        return doc

    @staticmethod
    def from_dict(data):
        return User(
            device_id=data.get("device_id"),
            username=data.get("username"),
            password=data.get("password"),
            email=data.get("email"),
            created_at=data.get("created_at"),
            id=data.get("_id")
        )
    
    @staticmethod
    def check_password(stored_password, password):
        return check_password_hash(stored_password, password)
    
    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)
    
    @staticmethod
    def get_by_username(username):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    @staticmethod
    def get_by_email(email):
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def save(self):
        if self.password and not self.password.startswith("scrypt:"):
            self.password = self.hash_password(self.password)
        user_dict = self.to_dict()
        result = mongo.db.users.insert_one(user_dict)
        self.id = result.inserted_id
        return str(self.id)