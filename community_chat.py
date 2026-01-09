"""
Universal Chat System for KropScan
Handles farmer-to-farmer communication in a single universal chat
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from user_management import UserManagement

class CommunityChat:
    """Manages universal chat features for farmer discussions"""

    def __init__(self, chat_file="community_chat.json", user_manager: UserManagement = None):
        self.chat_file = chat_file
        self.user_manager = user_manager or UserManagement()
        self.chat_data = self.load_chat_data()

        # Initialize universal chat
        if not self.chat_data or 'universal_chat' not in self.chat_data:
            self.chat_data['universal_chat'] = {
                "id": 1,
                "name": "Universal Community Chat",
                "description": "Main community chat for all farmers",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "members": [],  # All users are automatically members
                "messages": [],
                "is_public": True
            }
            self.save_chat_data()

    def load_chat_data(self) -> Dict:
        """Load community chat data from file"""
        if os.path.exists(self.chat_file):
            try:
                with open(self.chat_file, 'r') as f:
                    data = json.load(f)
                    # If data is a list (old format), convert to dict with universal chat
                    if isinstance(data, list):
                        # Convert old format to new format
                        if data:  # If there are old chat rooms
                            # Use the first room as the universal chat, or create a new one
                            if len(data) > 0 and isinstance(data[0], dict):
                                # Convert first room to universal chat format
                                old_room = data[0]
                                return {
                                    'universal_chat': {
                                        'id': old_room.get('id', 1),
                                        'name': old_room.get('name', 'Universal Community Chat'),
                                        'description': old_room.get('description', 'Main community chat for all farmers'),
                                        'created_at': old_room.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                        'members': old_room.get('members', []),
                                        'messages': old_room.get('messages', []),
                                        'is_public': old_room.get('is_public', True)
                                    }
                                }
                        # If no old rooms or invalid format, return empty dict to trigger initialization
                        return {}
                    # If data is already in the correct format
                    elif isinstance(data, dict):
                        # Convert old 'global_room' to 'universal_chat' if needed
                        if 'global_room' in data and 'universal_chat' not in data:
                            data['universal_chat'] = data.pop('global_room')
                        return data
                    else:
                        # If it's neither list nor dict, return empty dict
                        return {}
            except:
                return {}
        return {}

    def save_chat_data(self):
        """Save community chat data to file"""
        try:
            with open(self.chat_file, 'w') as f:
                json.dump(self.chat_data, f, indent=2)
        except Exception as e:
            print(f"Error saving chat data: {e}")

    def get_universal_chat(self) -> Dict:
        """Get the universal chat"""
        return self.chat_data.get('universal_chat', {})

    def join_universal_chat(self, user_id: str) -> bool:
        """Add a user to the universal chat"""
        universal_chat = self.get_universal_chat()
        if user_id not in universal_chat['members']:
            universal_chat['members'].append(user_id)
            self.save_chat_data()
        return True

    def send_message(self, user_id: str, message: str) -> bool:
        """Send a message to the universal chat"""
        universal_chat = self.get_universal_chat()

        # Get user name for display
        user_data = self.user_manager.get_user(user_id)
        user_name = user_data['name'] if user_data else "Unknown User"

        message_obj = {
            "id": len(universal_chat['messages']) + 1,
            "user_id": user_id,
            "user_name": user_name,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reactions": []
        }

        universal_chat['messages'].append(message_obj)
        self.save_chat_data()
        return True

    def get_messages(self, limit: int = 50) -> List[Dict]:
        """Get messages from the universal chat"""
        universal_chat = self.get_universal_chat()
        # Return the last 'limit' messages
        return universal_chat['messages'][-limit:]

    def add_reaction(self, message_id: int, user_id: str, reaction: str) -> bool:
        """Add a reaction to a message"""
        universal_chat = self.get_universal_chat()

        for message in universal_chat['messages']:
            if message['id'] == message_id:
                # Check if user already reacted
                existing_reaction = None
                for i, reaction_obj in enumerate(message['reactions']):
                    if reaction_obj['user_id'] == user_id:
                        existing_reaction = i
                        break

                if existing_reaction is not None:
                    # Update existing reaction
                    message['reactions'][existing_reaction]['reaction'] = reaction
                else:
                    # Add new reaction
                    message['reactions'].append({
                        'user_id': user_id,
                        'reaction': reaction,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                self.save_chat_data()
                return True
        return False

    def get_universal_chat_info(self) -> Dict:
        """Get universal chat information"""
        universal_chat = self.get_universal_chat()
        return {
            "name": universal_chat['name'],
            "description": universal_chat['description'],
            "created_at": universal_chat['created_at'],
            "member_count": len(universal_chat['members']),
            "message_count": len(universal_chat['messages'])
        }

# Example usage
if __name__ == "__main__":
    chat_system = CommunityChat()
    print("Universal chat system ready!")