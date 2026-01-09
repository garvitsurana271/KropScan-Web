import json
import os
from datetime import datetime

class TreatmentHistory:
    def __init__(self, history_file="treatment_history.json"):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def add_record(self, image_path, diagnosis, confidence, treatment, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "image_path": image_path,
            "diagnosis": diagnosis,
            "confidence": confidence,
            "treatment": treatment
        }
        
        self.history.append(record)
        self.save_history()
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)
    
    def get_history(self):
        return self.history
    
    def get_recent_records(self, limit=5):
        return self.history[-limit:] if len(self.history) >= limit else self.history

# Example usage
if __name__ == "__main__":
    history = TreatmentHistory()
    history.add_record(
        image_path="test_image.jpg",
        diagnosis="Tomato Early Blight",
        confidence=0.92,
        treatment="Apply copper-based fungicides immediately."
    )
    print("Recent records:", history.get_recent_records())