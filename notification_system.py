"""
Notification System for KropScan
Handles sending notifications to users about treatments, weather alerts, etc.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class Notification:
    """Represents a notification in the system"""
    
    def __init__(self, notification_id: str, user_id: str, title: str, message: str, 
                 notification_type: str = "info", priority: str = "normal"):
        self.id = notification_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = notification_type  # info, warning, alert, success
        self.priority = priority  # low, normal, high
        self.timestamp = datetime.now().isoformat()
        self.read = False
        self.sent = False
    
    def to_dict(self):
        """Convert notification to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'priority': self.priority,
            'timestamp': self.timestamp,
            'read': self.read,
            'sent': self.sent
        }

class NotificationSystem:
    """Manages sending and tracking notifications"""
    
    def __init__(self, notifications_file="notifications.json"):
        self.notifications_file = notifications_file
        self.notifications = self.load_notifications()
    
    def load_notifications(self) -> List[Dict]:
        """Load notifications from file"""
        if os.path.exists(self.notifications_file):
            try:
                with open(self.notifications_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_notifications(self):
        """Save notifications to file"""
        try:
            with open(self.notifications_file, 'w') as f:
                json.dump(self.notifications, f, indent=2)
        except Exception as e:
            print(f"Error saving notifications: {e}")
    
    def send_notification(self, user_id: str, title: str, message: str, 
                        notification_type: str = "info", priority: str = "normal") -> str:
        """Send a notification to a user"""
        import uuid
        notification_id = str(uuid.uuid4())
        
        notification = Notification(notification_id, user_id, title, message, notification_type, priority)
        self.notifications.append(notification.to_dict())
        self.save_notifications()
        
        return notification_id
    
    def get_user_notifications(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get notifications for a specific user"""
        user_notifications = [
            n for n in self.notifications 
            if n['user_id'] == user_id
        ]
        # Sort by timestamp, most recent first
        user_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        return user_notifications[:limit]
    
    def get_unread_notifications(self, user_id: str) -> List[Dict]:
        """Get unread notifications for a user"""
        return [
            n for n in self.notifications 
            if n['user_id'] == user_id and not n['read']
        ]
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                self.save_notifications()
                return True
        return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read"""
        count = 0
        for notification in self.notifications:
            if notification['user_id'] == user_id and not notification['read']:
                notification['read'] = True
                count += 1
        if count > 0:
            self.save_notifications()
        return count
    
    def send_weather_alert(self, user_id: str, location: str, alert_type: str, message: str):
        """Send a weather-related alert to a user"""
        title = f"Weather Alert - {alert_type.title()}"
        return self.send_notification(user_id, title, message, "warning", "high")
    
    def send_treatment_reminder(self, user_id: str, disease: str, treatment: str):
        """Send a treatment reminder to a user"""
        title = f"Treatment Reminder: {disease.replace('_', ' ').title()}"
        message = f"Reminder to apply: {treatment}"
        return self.send_notification(user_id, title, message, "info", "normal")
    
    def send_harvest_alert(self, user_id: str, crop: str):
        """Send a harvest timing alert to a user"""
        title = f"Harvest Alert: {crop.title()}"
        message = f"It's time to harvest your {crop.lower()}. Check for optimal ripeness indicators."
        return self.send_notification(user_id, title, message, "success", "normal")

# Example usage
if __name__ == "__main__":
    ns = NotificationSystem()
    
    # Send a test notification
    notification_id = ns.send_notification(
        user_id="test_user_123",
        title="Welcome to KropScan",
        message="Thank you for joining our platform. Start by scanning your first crop image.",
        notification_type="success"
    )
    
    print(f"Notification sent with ID: {notification_id}")
    
    # Send a weather alert
    weather_alert_id = ns.send_weather_alert(
        user_id="test_user_123",
        location="Maharashtra",
        alert_type="disease_risk",
        message="High humidity levels detected. Risk of fungal diseases increased. Apply preventive treatment."
    )
    
    print(f"Weather alert sent with ID: {weather_alert_id}")
    
    # Get user notifications
    user_notifications = ns.get_user_notifications("test_user_123")
    print(f"User has {len(user_notifications)} notifications")
    
    print("Notification system ready!")