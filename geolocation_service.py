import requests
import json
from typing import Dict, Optional, Tuple
import os

class GeolocationService:
    """
    Service to handle geolocation features and disease tracking by location
    """
    
    def __init__(self):
        # Disease tracking database
        self.disease_tracking_db = "disease_tracking.json"
        self.load_disease_tracking()
    
    def get_location_from_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get location details from coordinates using reverse geocoding
        """
        try:
            # Using OpenStreetMap Nominatim API (free)
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1"
            headers = {
                'User-Agent': 'KropScan/1.0 (https://krop-scan.com)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"⚠️ Geocoding API request failed: {e}")
            return None
    
    def get_coordinates_from_location(self, location_query: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates from location name using geocoding
        """
        try:
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={location_query}"
            headers = {
                'User-Agent': 'KropScan/1.0 (https://krop-scan.com)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"⚠️ Geocoding API request failed: {e}")
            return None
    
    def track_disease_outbreak(self, lat: float, lon: float, disease: str, confidence: float, 
                              image_path: Optional[str] = None, user_id: Optional[str] = None) -> bool:
        """
        Track a disease outbreak at specific location
        """
        try:
            location_info = self.get_location_from_coordinates(lat, lon)
            location_name = "Unknown"
            district = "Unknown"
            state = "Unknown"
            
            if location_info and 'address' in location_info:
                addr = location_info['address']
                location_name = addr.get('village', addr.get('town', addr.get('city', 'Unknown')))
                district = addr.get('county', addr.get('state_district', 'Unknown'))
                state = addr.get('state', 'Unknown')
            
            outbreak_record = {
                "timestamp": "2023-12-25T10:00:00Z",  # In real implementation, use current time
                "latitude": lat,
                "longitude": lon,
                "location_name": location_name,
                "district": district,
                "state": state,
                "disease": disease,
                "confidence": confidence,
                "image_path": image_path,
                "user_id": user_id
            }
            
            # Add to tracking database
            self.disease_tracking.append(outbreak_record)
            self.save_disease_tracking()
            
            return True
        except Exception as e:
            print(f"⚠️ Failed to track disease outbreak: {e}")
            return False
    
    def get_disease_heatmap_data(self, disease_type: Optional[str] = None) -> list:
        """
        Get disease tracking data for creating heatmaps
        """
        if disease_type:
            return [record for record in self.disease_tracking if record['disease'] == disease_type]
        return self.disease_tracking
    
    def get_regional_disease_stats(self, lat: float, lon: float, radius_km: float = 50) -> Dict:
        """
        Get disease statistics for a specific region
        """
        from math import radians, cos, sin, asin, sqrt
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """
            Calculate the great circle distance between two points 
            on the earth (specified in decimal degrees)
            """
            # Convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r
        
        # Filter records within the radius
        nearby_records = []
        for record in self.disease_tracking:
            distance = haversine_distance(
                lat, lon, 
                record['latitude'], record['longitude']
            )
            if distance <= radius_km:
                nearby_records.append(record)
        
        # Count disease occurrences
        disease_counts = {}
        for record in nearby_records:
            disease = record['disease']
            if disease in disease_counts:
                disease_counts[disease] += 1
            else:
                disease_counts[disease] = 1
        
        # Calculate statistics
        total_cases = len(nearby_records)
        stats = {
            "total_cases": total_cases,
            "disease_breakdown": disease_counts,
            "radius_km": radius_km,
            "center_location": {"lat": lat, "lon": lon}
        }
        
        return stats
    
    def load_disease_tracking(self):
        """
        Load disease tracking data from file
        """
        if os.path.exists(self.disease_tracking_db):
            try:
                with open(self.disease_tracking_db, 'r') as f:
                    self.disease_tracking = json.load(f)
            except:
                self.disease_tracking = []
        else:
            self.disease_tracking = []
    
    def save_disease_tracking(self):
        """
        Save disease tracking data to file
        """
        try:
            with open(self.disease_tracking_db, 'w') as f:
                json.dump(self.disease_tracking, f)
        except Exception as e:
            print(f"⚠️ Failed to save disease tracking data: {e}")

# Example usage
if __name__ == "__main__":
    geo_service = GeolocationService()
    
    # Example: Track a disease outbreak
    success = geo_service.track_disease_outbreak(
        lat=19.0760,  # Mumbai
        lon=72.8777,
        disease="Tomato Early Blight",
        confidence=0.85,
        user_id="user123"
    )
    
    print("Disease tracking success:", success)
    
    # Get regional stats
    stats = geo_service.get_regional_disease_stats(19.0760, 72.8777, 100)
    print("Regional disease stats:", stats)