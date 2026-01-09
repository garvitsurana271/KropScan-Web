"""
Authentication System for KropScan
Handles user registration, login, and session management
"""
import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from user_management import UserManagement

class AuthSystem:
    """Handles user authentication and session management"""

    def __init__(self, users_file="users.json", sessions_file="sessions.json", admin_email="admin@kropscan.ai", admin_password="admin123"):
        self.users_file = users_file
        self.sessions_file = sessions_file
        self.user_manager = UserManagement(users_file)
        self.sessions = self.load_sessions()

        # Initialize admin account if it doesn't exist
        self.admin_email = admin_email
        self.admin_password = admin_password
        self.initialize_admin_account()

    def initialize_admin_account(self):
        """Initialize admin account if it doesn't exist"""
        # Check if admin account already exists
        for user_id, user_data in self.user_manager.users.items():
            if user_data.get('email') == self.admin_email:
                # Ensure this user is marked as admin
                if not user_data.get('is_admin', False):
                    user_data['is_admin'] = True
                    self.user_manager.save_users()
                return

        # Create admin account
        admin_user_id = self.user_manager.register_user(
            "Admin User",
            "9999999999",  # Phone
            "KropScan Admin",  # Location
            0.0  # Farm size
        )

        if admin_user_id:
            # Set admin-specific data
            self.user_manager.users[admin_user_id]['email'] = self.admin_email
            self.user_manager.users[admin_user_id]['password'] = self.hash_password(self.admin_password)
            self.user_manager.users[admin_user_id]['is_admin'] = True
            self.user_manager.users[admin_user_id]['created_at'] = datetime.now().isoformat()
            self.user_manager.users[admin_user_id]['last_login'] = None
            self.user_manager.users[admin_user_id]['preferences'] = {
                'theme': 'default',
                'language': 'en',
                'notifications_enabled': True
            }
            self.user_manager.save_users()

    def load_sessions(self) -> Dict:
        """Load active sessions from file"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_sessions(self):
        """Save active sessions to file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
        return salt + pwdhash.hex()
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        salt = stored_hash[:32]
        stored_pwdhash = stored_hash[32:]
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                      password.encode('utf-8'),
                                      salt.encode('utf-8'),
                                      100000)
        return pwdhash.hex() == stored_pwdhash
    
    def register_user(self, name: str, email: str, phone: str, password: str, location: str, farm_size: float = 0.0, is_admin: bool = False) -> Optional[str]:
        """Register a new user"""
        # Check if email already exists
        for user_id, user_data in self.user_manager.users.items():
            if user_data.get('email') == email:
                return None  # Email already exists

        # Hash the password
        hashed_password = self.hash_password(password)

        # Register user with user management system
        user_id = self.user_manager.register_user(name, phone, location, farm_size)

        if user_id:
            # Add email and password to user data
            self.user_manager.users[user_id]['email'] = email
            self.user_manager.users[user_id]['password'] = hashed_password
            self.user_manager.users[user_id]['is_admin'] = is_admin  # Set admin status
            self.user_manager.users[user_id]['created_at'] = datetime.now().isoformat()
            self.user_manager.users[user_id]['last_login'] = None
            self.user_manager.users[user_id]['preferences'] = {
                'theme': 'default',
                'language': 'en',
                'notifications_enabled': True
            }
            self.user_manager.save_users()
            return user_id

        return None
    
    def login_user(self, email: str, password: str) -> Optional[str]:
        """Login user and return session token"""
        # Find user by email
        user_id = None
        for uid, user_data in self.user_manager.users.items():
            if user_data.get('email') == email:
                user_id = uid
                break

        if not user_id:
            return None

        # Verify password
        stored_hash = self.user_manager.users[user_id]['password']
        if not self.verify_password(password, stored_hash):
            return None

        # Update last login
        self.user_manager.users[user_id]['last_login'] = datetime.now().isoformat()
        self.user_manager.save_users()

        # Create session
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat(),  # 7 days expiry
            'is_admin': self.user_manager.users[user_id].get('is_admin', False)  # Include admin status
        }
        self.save_sessions()

        return session_token

    def is_admin(self, session_token: str) -> bool:
        """Check if user is admin based on session token"""
        if session_token in self.sessions:
            return self.sessions[session_token].get('is_admin', False)
        return False
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by removing session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            self.save_sessions()
            return True
        return False
    
    def get_user_from_session(self, session_token: str) -> Optional[Dict]:
        """Get user data from session token"""
        if session_token not in self.sessions:
            return None

        session_data = self.sessions[session_token]
        user_id = session_data['user_id']

        # Check if session is expired
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        if datetime.now() > expires_at:
            self.logout_user(session_token)
            return None

        user_data = self.user_manager.get_user(user_id)
        if user_data:
            # Include admin status from session
            user_data['is_admin'] = session_data.get('is_admin', False)

        return user_data
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user preferences"""
        if user_id in self.user_manager.users:
            if 'preferences' not in self.user_manager.users[user_id]:
                self.user_manager.users[user_id]['preferences'] = {}
            self.user_manager.users[user_id]['preferences'].update(preferences)
            self.user_manager.save_users()
            return True
        return False
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        user = self.user_manager.get_user(user_id)
        if user:
            return user.get('preferences', {})
        return {}

# Example usage
if __name__ == "__main__":
    auth = AuthSystem()
    
    # Register a new user
    user_id = auth.register_user(
        name="Ramesh Kumar",
        email="ramesh@example.com",
        phone="9876543210",
        password="securepassword123",
        location="Maharashtra, India",
        farm_size=2.5
    )
    
    if user_id:
        print(f"User registered with ID: {user_id}")
        
        # Login the user
        session_token = auth.login_user("ramesh@example.com", "securepassword123")
        if session_token:
            print(f"User logged in with session: {session_token[:10]}...")
            
            # Get user data from session
            user_data = auth.get_user_from_session(session_token)
            print(f"User data: {user_data['name']}")
            
            # Update preferences
            auth.update_user_preferences(user_data['user_id'], {'theme': 'dark', 'language': 'hi'})
            print("Preferences updated")
    
    print("Authentication system ready!")