import torch
import os
import json
from typing import Dict, Optional, Tuple
from PIL import Image
import torchvision.transforms as transforms
import numpy as np

class OfflineMode:
    """
    Offline mode for KropScan when internet is not available
    """
    
    def __init__(self, offline_model_path: str = "offline_model.pth", 
                 treatment_db_path: str = "treatment_database.json"):
        self.offline_model_path = offline_model_path
        self.treatment_db_path = treatment_db_path
        self.offline_model = None
        self.treatment_database = {}
        self.is_available = self._check_availability()
        
        if self.is_available:
            self._load_offline_model()
            self._load_treatment_database()
    
    def _check_availability(self) -> bool:
        """
        Check if offline model and treatment database are available
        """
        model_exists = os.path.exists(self.offline_model_path)
        db_exists = os.path.exists(self.treatment_db_path)
        
        if not model_exists:
            print(f"! Offline model not found: {self.offline_model_path}")
        if not db_exists:
            print(f"! Treatment database not found: {self.treatment_db_path}")
        
        return model_exists and db_exists
    
    def _load_offline_model(self):
        """
        Load the lightweight offline model
        """
        try:
            # Load model with CPU device for offline use
            self.offline_model = torch.load(self.offline_model_path, map_location='cpu')
            self.offline_model.eval()
            print("✅ Offline model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading offline model: {e}")
            self.offline_model = None
    
    def _load_treatment_database(self):
        """
        Load the treatment database for offline use
        """
        try:
            with open(self.treatment_db_path, 'r') as f:
                self.treatment_database = json.load(f)
            print("✅ Treatment database loaded successfully")
        except Exception as e:
            print(f"❌ Error loading treatment database: {e}")
            self.treatment_database = {}
    
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """
        Preprocess image for offline model
        """
        # Define transforms similar to online model
        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),  # Smaller size for faster offline processing
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        image = Image.open(image_path).convert('RGB')
        return preprocess(image).unsqueeze(0)  # Add batch dimension
    
    def predict_offline(self, image_path: str) -> Optional[Tuple[str, float, str]]:
        """
        Make prediction using offline model
        Returns: (disease_name, confidence, treatment_text)
        """
        if not self.is_available or self.offline_model is None:
            return None
        
        try:
            # Preprocess image
            input_tensor = self.preprocess_image(image_path)
            
            # Run inference
            with torch.no_grad():
                outputs = self.offline_model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                
                # Get top prediction
                confidence, predicted_idx = torch.max(probabilities, 0)
                confidence = confidence.item()
                
                # In a real implementation, we would have class names
                # For now, we'll return a placeholder
                class_names = list(self.treatment_database.keys()) if self.treatment_database else ["Unknown"]
                
                if predicted_idx < len(class_names):
                    disease_name = class_names[predicted_idx]
                else:
                    disease_name = "Unknown"
                
                # Get treatment information
                treatment_info = self.treatment_database.get(disease_name, 
                    {"treatment": "Offline treatment information not available. Please connect to internet for full details."})
                
                treatment_text = treatment_info.get("treatment", 
                    "Offline treatment information not available. Please connect to internet for full details.")
                
                return disease_name, confidence, treatment_text
        except Exception as e:
            print(f"❌ Error during offline prediction: {e}")
            return None
    
    def cache_prediction_for_sync(self, image_path: str, prediction: Tuple[str, float, str], 
                                  location: str = None):
        """
        Cache offline prediction to sync when internet is available
        """
        cache_entry = {
            "image_path": image_path,
            "prediction": {
                "disease": prediction[0],
                "confidence": prediction[1],
                "treatment": prediction[2]
            },
            "timestamp": "2023-12-25T10:00:00Z",  # In real implementation, use current time
            "location": location,
            "synced": False
        }
        
        # Add to offline cache
        cache_file = "offline_cache.json"
        cache_data = []
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
            except:
                cache_data = []
        
        cache_data.append(cache_entry)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"❌ Error caching prediction: {e}")
    
    def get_cached_predictions(self) -> list:
        """
        Get all cached predictions that need to be synced
        """
        cache_file = "offline_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def sync_cached_predictions(self, online_endpoint: str):
        """
        Sync cached predictions to online system when internet is available
        """
        cached_predictions = self.get_cached_predictions()
        synced_count = 0
        
        for prediction in cached_predictions:
            if not prediction.get("synced", False):
                # In a real implementation, we would send this to the online endpoint
                # For now, we'll just mark it as synced
                prediction["synced"] = True
                synced_count += 1
        
        # Save updated cache
        cache_file = "offline_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(cached_predictions, f)
        except Exception as e:
            print(f"❌ Error updating cache: {e}")
        
        return synced_count
    
    def create_lightweight_model(self, original_model_path: str, output_path: str):
        """
        Create a lightweight version of the model for offline use
        This is a simplified version - in practice, you'd use model compression techniques
        """
        try:
            # Load original model
            original_model = torch.load(original_model_path, map_location='cpu')
            
            # For this example, we'll just save the model as is
            # In a real implementation, you might:
            # - Quantize the model (torch.quantization)
            # - Prune less important weights
            # - Use knowledge distillation to create a smaller model
            torch.save(original_model, output_path)
            
            print(f"✅ Lightweight model created at: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating lightweight model: {e}")
            return False
    
    def is_offline_mode_available(self) -> bool:
        """
        Check if offline mode is available
        """
        return self.is_available

# Example usage
if __name__ == "__main__":
    offline = OfflineMode()
    
    if offline.is_offline_mode_available():
        print("Offline mode is available")
        
        # Example prediction (would need actual image file)
        # result = offline.predict_offline("path/to/image.jpg")
        # if result:
        #     disease, confidence, treatment = result
        #     print(f"Predicted: {disease} with {confidence:.2f} confidence")
        #     print(f"Treatment: {treatment}")
    else:
        print("Offline mode is not available - model or database files missing")