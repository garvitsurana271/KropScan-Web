import requests
import os
from typing import Dict, Optional

class WeatherService:
    """
    Weather service using OpenWeatherMap's free API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Use environment variable or default to a demo key (replace with your own)
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "demo") 
        if self.api_key == "demo":
            print("! Weather API key not set. Weather features will use demo data.")
            print("To enable weather features, set OPENWEATHER_API_KEY environment variable")
            print("Sign up for free API key at: https://openweathermap.org/api")
    
    def get_weather_info(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather information for a location using OpenWeatherMap API
        """
        if not self.api_key or self.api_key == "demo":
            # Return demo data
            return {
                "main": {"temp": 28.5, "humidity": 75},
                "weather": [{"main": "Clouds", "description": "scattered clouds"}],
                "wind": {"speed": 3.5},
                "name": "Demo Location"
            }
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"! Weather API request failed: {e}")
            return None
        except Exception as e:
            print(f"! Unexpected error in weather service: {e}")
            return None
    
    def get_disease_risk_from_weather(self, weather_data: Dict) -> Dict:
        """
        Analyze weather data to determine disease risk levels
        """
        if not weather_data:
            return {
                "fungal_risk": "unknown",
                "bacterial_risk": "unknown",
                "general_risk": "unknown",
                "message": "Weather data unavailable"
            }
        
        # Extract relevant weather data
        temp = weather_data.get("main", {}).get("temp", 25)
        humidity = weather_data.get("main", {}).get("humidity", 60)
        precipitation = weather_data.get("rain", {}).get("1h", 0) if weather_data.get("rain") else 0
        weather_main = weather_data.get("weather", [{}])[0].get("main", "").lower()
        
        # Determine risk levels based on weather conditions
        fungal_risk = self._calculate_fungal_risk(temp, humidity, precipitation, weather_main)
        bacterial_risk = self._calculate_bacterial_risk(temp, humidity, precipitation, weather_main)
        general_risk = max(fungal_risk, bacterial_risk, key=lambda x: ["low", "medium", "high", "very_high"].index(x) if x in ["low", "medium", "high", "very_high"] else 0)
        
        risk_messages = {
            "low": "Low risk for disease development today",
            "medium": "Moderate risk - monitor crops closely",
            "high": "High risk - consider preventive measures",
            "very_high": "Very high risk - take immediate action"
        }
        
        return {
            "fungal_risk": fungal_risk,
            "bacterial_risk": bacterial_risk,
            "general_risk": general_risk,
            "temperature": temp,
            "humidity": humidity,
            "precipitation_1h": precipitation,
            "weather_condition": weather_main,
            "message": risk_messages.get(general_risk, "Risk assessment unavailable")
        }
    
    def _calculate_fungal_risk(self, temp: float, humidity: float, precipitation: float, weather_main: str) -> str:
        """
        Calculate fungal disease risk based on weather conditions
        """
        risk_score = 0
        
        # Temperature factor (fungal diseases thrive in moderate temperatures)
        if 15 <= temp <= 30:
            risk_score += 2
        elif 10 <= temp <= 35:
            risk_score += 1
        
        # Humidity factor (high humidity promotes fungal growth)
        if humidity > 80:
            risk_score += 3
        elif humidity > 60:
            risk_score += 2
        elif humidity > 40:
            risk_score += 1
        
        # Precipitation factor (moisture is critical for fungal spores)
        if precipitation > 5:
            risk_score += 3
        elif precipitation > 1:
            risk_score += 2
        elif precipitation > 0:
            risk_score += 1
            
        # Weather condition factor
        if "rain" in weather_main or "cloud" in weather_main:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 7:
            return "very_high"
        elif risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _calculate_bacterial_risk(self, temp: float, humidity: float, precipitation: float, weather_main: str) -> str:
        """
        Calculate bacterial disease risk based on weather conditions
        """
        risk_score = 0
        
        # Temperature factor (bacterial diseases thrive in warm conditions)
        if 25 <= temp <= 35:
            risk_score += 2
        elif 20 <= temp <= 40:
            risk_score += 1
        
        # Humidity factor (high humidity promotes bacterial growth)
        if humidity > 70:
            risk_score += 2
        elif humidity > 50:
            risk_score += 1
        
        # Precipitation factor (free moisture allows bacterial entry)
        if precipitation > 2:
            risk_score += 2
        elif precipitation > 0:
            risk_score += 1
            
        # Weather condition factor
        if "rain" in weather_main:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "medium"
        elif risk_score >= 1:
            return "low"
        else:
            return "very_low"

# Example usage
if __name__ == "__main__":
    # Example without API key (will show demo data)
    weather_service = WeatherService()
    
    # Example with mock data
    mock_weather = {
        "main": {"temp": 25, "humidity": 85},
        "weather": [{"main": "Rain"}],
        "rain": {"1h": 3}
    }
    
    risk = weather_service.get_disease_risk_from_weather(mock_weather)
    print("Disease risk based on weather:", risk)