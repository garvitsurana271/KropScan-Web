"""
User Management System for KropScan
Handles farmer registration, profiles, and treatment history
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class User:
    """Represents a user (farmer) in the system"""
    
    def __init__(self, user_id: str, name: str, phone: str, location: str, farm_size: float = 0.0):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.location = location
        self.farm_size = farm_size
        self.registration_date = datetime.now().isoformat()
        self.treatment_history = []
        self.notifications = []
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'location': self.location,
            'farm_size': self.farm_size,
            'registration_date': self.registration_date,
            'treatment_history': self.treatment_history,
            'notifications': self.notifications
        }

class UserManagement:
    """Manages user registration, profiles, and treatment history"""
    
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.users = self.load_users()
    
    def load_users(self) -> Dict:
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def register_user(self, name: str, phone: str, location: str, farm_size: float = 0.0) -> Optional[str]:
        """Register a new user and return user ID"""
        user_id = str(uuid.uuid4())
        
        user = User(user_id, name, phone, location, farm_size)
        self.users[user_id] = user.to_dict()
        self.save_users()
        
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user_profile(self, user_id: str, **kwargs) -> bool:
        """Update user profile information"""
        if user_id in self.users:
            for key, value in kwargs.items():
                if key in ['name', 'phone', 'location', 'farm_size']:
                    self.users[user_id][key] = value
            self.save_users()
            return True
        return False
    
    def add_treatment_to_history(self, user_id: str, treatment_record: Dict) -> bool:
        """Add a treatment record to user's history"""
        if user_id in self.users:
            # Add timestamp to the record
            treatment_record['timestamp'] = datetime.now().isoformat()
            self.users[user_id]['treatment_history'].append(treatment_record)
            self.save_users()
            return True
        return False
    
    def get_user_treatment_history(self, user_id: str) -> List[Dict]:
        """Get treatment history for a user"""
        user = self.get_user(user_id)
        return user.get('treatment_history', []) if user else []
    
    def send_notification(self, user_id: str, message: str, notification_type: str = "info") -> bool:
        """Send a notification to a user"""
        if user_id in self.users:
            notification = {
                'id': str(uuid.uuid4()),
                'message': message,
                'type': notification_type,
                'timestamp': datetime.now().isoformat(),
                'read': False
            }
            self.users[user_id]['notifications'].append(notification)
            self.save_users()
            return True
        return False
    
    def get_unread_notifications(self, user_id: str) -> List[Dict]:
        """Get unread notifications for a user"""
        user = self.get_user(user_id)
        if user:
            return [n for n in user['notifications'] if not n.get('read', True)]
        return []
    
    def mark_notification_as_read(self, user_id: str, notification_id: str) -> bool:
        """Mark a notification as read"""
        if user_id in self.users:
            for notification in self.users[user_id]['notifications']:
                if notification['id'] == notification_id:
                    notification['read'] = True
                    self.save_users()
                    return True
        return False

# Example usage
if __name__ == "__main__":
    um = UserManagement()
    
    # Register a new user
    user_id = um.register_user(
        name="Ramesh Kumar",
        phone="9876543210",
        location="Maharashtra, India",
        farm_size=2.5  # acres
    )
    
    print(f"User registered with ID: {user_id}")
    
    # Add a treatment to history
    if user_id:
        um.add_treatment_to_history(
            user_id,
            {
                'disease': 'Tomato Early Blight',
                'treatment': 'Copper-based fungicide',
                'confidence': 0.85,
                'date': '2023-12-25'
            }
        )
        
        # Get user's treatment history
        history = um.get_user_treatment_history(user_id)
        print(f"User treatment history: {history}")
    
    print("User management system ready!")