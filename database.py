import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class UserDatabase:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {"users": {}, "admin_messages": {}}
        return {"users": {}, "admin_messages": {}}
    
    def _save_data(self):
        """Save data to JSON file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add a new user to the database"""
        if str(user_id) not in self.data["users"]:
            self.data["users"][str(user_id)] = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "joined_date": datetime.now().isoformat(),
                "messages": [],
                "is_active": True
            }
            self._save_data()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        return self.data["users"].get(str(user_id))
    
    def add_message(self, user_id: int, message_text: str, is_from_admin: bool = False):
        """Add a message to user's chat history"""
        user = self.get_user(user_id)
        if user:
            message = {
                "text": message_text,
                "timestamp": datetime.now().isoformat(),
                "is_from_admin": is_from_admin
            }
            user["messages"].append(message)
            self._save_data()
    
    def get_user_messages(self, user_id: int) -> List[Dict]:
        """Get all messages for a user"""
        user = self.get_user(user_id)
        return user["messages"] if user else []
    
    def get_all_users(self) -> List[Dict]:
        """Get all active users"""
        return [user for user in self.data["users"].values() if user.get("is_active", True)]
    
    def deactivate_user(self, user_id: int):
        """Deactivate a user"""
        if str(user_id) in self.data["users"]:
            self.data["users"][str(user_id)]["is_active"] = False
            self._save_data()
    
    def activate_user(self, user_id: int):
        """Activate a user"""
        if str(user_id) in self.data["users"]:
            self.data["users"][str(user_id)]["is_active"] = True
            self._save_data() 