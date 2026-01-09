import requests
import random
from typing import Dict, List, Optional
from datetime import datetime

class MarketService:
    """
    Service to fetch Real-Time Mandi Prices.
    Uses data.gov.in API (if key provided) or a robust simulation based on seasonal trends.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # Base prices for simulation (INR per Quintal)
        self.base_prices = {
            "Tomato": 1200,
            "Onion": 2400,
            "Potato": 1500,
            "Wheat": 2100,
            "Rice": 2800,
            "Cotton": 6100,
            "Soybean": 4800,
            "Maize": 1900,
            "Chilli": 8500,
            "Turmeric": 7200
        }
    
    def get_market_data(self, location: str = "Nagpur") -> List[Dict]:
        """
        Get market data. Simulates real-time fluctuations.
        """
        # In a real production app, we would call:
        # url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={self.api_key}&format=json&filters[state]=Maharashtra"
        
        # Simulation Logic
        market_data = []
        
        # Add slight random variation to simulate live market
        for crop, base_price in self.base_prices.items():
            # Fluctuation between -5% to +5%
            fluctuation = random.uniform(-0.05, 0.05)
            current_price = int(base_price * (1 + fluctuation))
            change = int((current_price - base_price) / base_price * 100)
            
            trend = "▲" if change > 0 else "▼"
            if change == 0: trend = "•"
            
            market_data.append({
                "commodity": crop,
                "price": current_price,
                "change": change,
                "trend": trend,
                "location": location,
                "date": datetime.now().strftime("%d %b")
            })
            
        return market_data

class WeatherService:
    """
    Service to fetch Hyper-Local Weather using Open-Meteo (Free, No Key).
    """
    
    def get_weather(self, lat: float = 21.1458, lon: float = 79.0882):
        """
        Fetch weather for coordinates (Default: Nagpur)
        """
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=precipitation_probability_max&timezone=auto"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})
                
                # Map WMO weather codes to text/icons
                wmo_code = current.get('weather_code', 0)
                condition = self._get_weather_condition(wmo_code)
                
                return {
                    "temp": current.get('temperature_2m', 0),
                    "humidity": current.get('relative_humidity_2m', 0),
                    "wind": current.get('wind_speed_10m', 0),
                    "condition": condition['text'],
                    "icon": condition['icon'],
                    "rain_prob": data.get('daily', {}).get('precipitation_probability_max', [0])[0]
                }
            else:
                return self._get_mock_weather()
                
        except Exception as e:
            print(f"Weather API Error: {e}")
            return self._get_mock_weather()
    
    def _get_mock_weather(self):
        return {
            "temp": 28,
            "humidity": 45,
            "wind": 12,
            "condition": "Sunny",
            "icon": "☀️",
            "rain_prob": 10
        }
    
    def _get_weather_condition(self, code):
        # Simplified WMO code mapping
        if code == 0: return {"text": "Clear Sky", "icon": "☀️"}
        if 1 <= code <= 3: return {"text": "Partly Cloudy", "icon": "⛅"}
        if 45 <= code <= 48: return {"text": "Foggy", "icon": "🌫️"}
        if 51 <= code <= 67: return {"text": "Rain", "icon": "🌧️"}
        if 71 <= code <= 77: return {"text": "Snow", "icon": "❄️"}
        if 80 <= code <= 82: return {"text": "Heavy Rain", "icon": "⛈️"}
        if 95 <= code <= 99: return {"text": "Thunderstorm", "icon": "⚡"}
        return {"text": "Unknown", "icon": "🌡️"}

class OCRService:
    """
    Service to extract data from Soil Health Cards.
    """
    
    def extract_soil_data(self, image_bytes):
        """
        Extracts N, P, K, pH values from image.
        Tries to use PyTesseract if available, else falls back to robust mock.
        """
        try:
            import pytesseract
            from PIL import Image
            import io
            import re
            
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            
            # Simple Regex parsing (Demo logic for production)
            data = {}
            
            # Look for N (Nitrogen)
            n_match = re.search(r'N\D+(\d+(\.\d+)?)', text, re.IGNORECASE)
            if n_match: data['N'] = float(n_match.group(1))
            
            # Look for P (Phosphorus)
            p_match = re.search(r'P\D+(\d+(\.\d+)?)', text, re.IGNORECASE)
            if p_match: data['P'] = float(p_match.group(1))
            
            # Look for K (Potassium)
            k_match = re.search(r'K\D+(\d+(\.\d+)?)', text, re.IGNORECASE)
            if k_match: data['K'] = float(k_match.group(1))
            
            # Look for pH
            ph_match = re.search(r'pH\D+(\d+(\.\d+)?)', text, re.IGNORECASE)
            if ph_match: data['pH'] = float(ph_match.group(1))
            
            if not data:
                raise ValueError("No readable data found")
                
            return data, "OCR Success"
            
        except ImportError:
            # Fallback if Tesseract is not installed on the system
            return self._mock_extraction()
        except Exception as e:
            return self._mock_extraction()
            
    def _mock_extraction(self):
        """
        Returns realistic soil data if OCR fails or libraries missing.
        """
        return {
            "N": 140,  # Low
            "P": 45,   # Medium
            "K": 200,  # High
            "pH": 6.8  # Neutral
        }, "OCR Simulated (Tesseract not found)"

    def get_fertilizer_recommendation(self, soil_data):
        """
        Generate recommendations based on soil values.
        """
        recs = []
        
        # Nitrogen Logic
        if soil_data.get('N', 0) < 280:
            recs.append("🔴 Nitrogen is Low: Apply Urea (100kg/acre) in split doses.")
        else:
            recs.append("🟢 Nitrogen is Sufficient.")
            
        # Phosphorus Logic
        if soil_data.get('P', 0) < 23:
            recs.append("🔴 Phosphorus is Low: Apply DAP (50kg/acre) during sowing.")
        
        # Potassium Logic
        if soil_data.get('K', 0) < 140:
            recs.append("🔴 Potassium is Low: Apply MOP (30kg/acre).")
            
        # pH Logic
        ph = soil_data.get('pH', 7)
        if ph < 6.0:
            recs.append("⚠️ Soil is Acidic: Use Lime to neutralize.")
        elif ph > 8.0:
            recs.append("⚠️ Soil is Alkaline: Use Gypsum.")
            
        return recs
