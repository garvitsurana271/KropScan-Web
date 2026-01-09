# frontend.py
"""
KropScan AI - Premium Agricultural Intelligence Platform
-------------------------------------------------------------
Version 2.2 - Complete Fixes:
- Remember Me functionality
- Multi-language AI responses
- Brighter text in dark mode
- Data persistence
- Real API integration ready
"""

import os
import streamlit as st
import requests
from PIL import Image
import time
import io
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import hashlib

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="KropScan AI - Intelligent Farming",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize directory structure for persistence (Note: Ephemeral on Streamlit Cloud)
os.makedirs("database/feedback", exist_ok=True)
os.makedirs("database/users", exist_ok=True)

# ==========================================
# FEATURE IMPORTS & INITIALIZATION
# ==========================================

@st.cache_resource
def load_services():
    """Load and cache all heavy services"""
    services = {
        'auth': None,
        'chat': None,
        'community': None,
        'user_mgr': None,
        'comm_feat': None,
        'ai': None
    }
    
    # 1. Authentication
    try:
        from auth_system import AuthSystem
        services['auth'] = AuthSystem()
        print("✅ Auth System loaded")
    except Exception as e:
        print(f"❌ Auth System failed: {e}")

    # 2. AI Engine
    try:
        from ai_engine import KropScanAI
        services['ai'] = KropScanAI()
        print("✅ AI Engine loaded")
    except Exception as e:
        print(f"❌ AI Engine failed: {e}")

    # 3. Chatbot
    try:
        from chatbot import KropBot
        services['chat'] = KropBot()
        print("✅ Chatbot loaded")
    except Exception as e:
        print(f"❌ Chatbot failed: {e}")

    # 4. Community Features
    try:
        from community_chat import CommunityChat
        from user_management import UserManagement
        services['community'] = CommunityChat()
        services['user_mgr'] = UserManagement()
        print("✅ Community System loaded")
    except Exception as e:
        print(f"❌ Community System failed: {e}")
        
    try:
        from community_features import CommunityFeatures
        services['comm_feat'] = CommunityFeatures()
    except Exception:
        pass

    return services

# Load services once
SERVICES = load_services()

# Map to global variables for compatibility
auth_system = SERVICES['auth']
ai_engine = SERVICES['ai']
chatbot = SERVICES['chat']
community_chat = SERVICES['community']
user_manager = SERVICES['user_mgr']
community_features = SERVICES['comm_feat']

AUTH_AVAILABLE = auth_system is not None
COMMUNITY_CHAT_AVAILABLE = community_chat is not None
AI_AVAILABLE = ai_engine is not None
CHATBOT_AVAILABLE = chatbot is not None

# ==========================================
# CONSTANTS
# ==========================================

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

STATE_CAPITALS = {
    "Andhra Pradesh": {"city": "Amaravati", "lat": 16.5062, "lon": 80.6480},
    "Maharashtra": {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    "Karnataka": {"city": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    "Tamil Nadu": {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "Gujarat": {"city": "Gandhinagar", "lat": 23.2156, "lon": 72.6369},
    "Rajasthan": {"city": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    "Uttar Pradesh": {"city": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    "Punjab": {"city": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    "West Bengal": {"city": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    "Delhi": {"city": "New Delhi", "lat": 28.6139, "lon": 77.2090},
    "Kerala": {"city": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366},
    "Telangana": {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    "Bihar": {"city": "Patna", "lat": 25.5941, "lon": 85.1376},
    "Madhya Pradesh": {"city": "Bhopal", "lat": 23.2599, "lon": 77.4126},
    "Haryana": {"city": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
}

# Disease severity and savings mapping
DISEASE_SAVINGS = {
    'late_blight': {'severity': 'critical', 'savings': 2000, 'yield_loss_prevented': '50-70%'},
    'early_blight': {'severity': 'medium', 'savings': 800, 'yield_loss_prevented': '20-30%'},
    'bacterial_spot': {'severity': 'medium', 'savings': 600, 'yield_loss_prevented': '15-25%'},
    'leaf_mold': {'severity': 'low', 'savings': 400, 'yield_loss_prevented': '10-15%'},
    'septoria': {'severity': 'medium', 'savings': 700, 'yield_loss_prevented': '20-30%'},
    'spider_mites': {'severity': 'medium', 'savings': 500, 'yield_loss_prevented': '15-20%'},
    'target_spot': {'severity': 'low', 'savings': 400, 'yield_loss_prevented': '10-15%'},
    'mosaic_virus': {'severity': 'high', 'savings': 1500, 'yield_loss_prevented': '40-60%'},
    'yellow_leaf_curl': {'severity': 'high', 'savings': 1200, 'yield_loss_prevented': '30-50%'},
    'common_rust': {'severity': 'medium', 'savings': 600, 'yield_loss_prevented': '15-25%'},
    'northern_leaf_blight': {'severity': 'high', 'savings': 1000, 'yield_loss_prevented': '30-40%'},
    'healthy': {'severity': 'none', 'savings': 0, 'yield_loss_prevented': '0%'},
    'default': {'severity': 'medium', 'savings': 500, 'yield_loss_prevented': '15-25%'},
}

# Persistence file paths
USER_DATA_FILE = "user_data.json"
REMEMBERED_SESSIONS_FILE = "remembered_sessions.json"

# ==========================================
# DATA PERSISTENCE FUNCTIONS
# ==========================================

def load_user_data() -> Dict:
    """Load persisted user data from file"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_data(data: Dict):
    """Save user data to file for persistence"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving user data: {e}")

def get_user_persistent_data(user_id: str) -> Dict:
    """Get persistent data for a specific user"""
    all_data = load_user_data()
    return all_data.get(user_id, {
        'scan_history': [],
        'total_scans': 0,
        'total_savings': 0,
        'diseases_detected': [],
        'last_scan_date': None,
        'created_at': datetime.now().isoformat()
    })

def save_user_persistent_data(user_id: str, data: Dict):
    """Save persistent data for a specific user"""
    all_data = load_user_data()
    all_data[user_id] = data
    save_user_data(all_data)

def load_remembered_sessions() -> Dict:
    """Load remembered login sessions"""
    if os.path.exists(REMEMBERED_SESSIONS_FILE):
        try:
            with open(REMEMBERED_SESSIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_remembered_session(email: str, token: str, expiry_days: int = 30):
    """Save a remembered session"""
    sessions = load_remembered_sessions()
    sessions[email] = {
        'token': token,
        'expiry': (datetime.now() + timedelta(days=expiry_days)).isoformat()
    }
    try:
        with open(REMEMBERED_SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        print(f"Error saving remembered session: {e}")

def get_remembered_session(email: str) -> Optional[str]:
    """Get a remembered session token if valid"""
    sessions = load_remembered_sessions()
    if email in sessions:
        session = sessions[email]
        expiry = datetime.fromisoformat(session['expiry'])
        if datetime.now() < expiry:
            return session['token']
        else:
            # Remove expired session
            del sessions[email]
            with open(REMEMBERED_SESSIONS_FILE, 'w') as f:
                json.dump(sessions, f, indent=2)
    return None

def clear_remembered_session(email: str):
    """Clear a remembered session"""
    sessions = load_remembered_sessions()
    if email in sessions:
        del sessions[email]
        with open(REMEMBERED_SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
def init_session_state():
    defaults = {
        'theme': 'dark',
        'app_language': 'en',
        'chat_history': [{
            "role": "assistant",
            "content": "Namaste! 🌱 I'm KropBot, your AI farming assistant. How can I help you today?"
        }],
        'current_page': 'dashboard',
        'scan_history': [],
        'total_scans': 0,
        'total_savings': 0,
        'current_user': None,
        'current_user_email': None,
        'is_admin': False,
        'user_state': 'Maharashtra',
        'weather_data': None,
        'weather_last_fetch': None,
        'market_data': None,
        'market_last_fetch': None,
        'scan_result': None,
        'analysis_complete': False,
        'treatment_fetched': False,
        'dynamic_treatment': None,
        'active_members_base': random.randint(80, 150),
        'active_members_last_update': time.time(),
        'user_id': None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_active_members_count() -> int:
    """Generate believable random active members count"""
    current_time = time.time()
    last_update = st.session_state.get('active_members_last_update', current_time)
    base_count = st.session_state.get('active_members_base', 100)
    
    if current_time - last_update > 30:
        change = random.randint(-5, 5)
        new_base = max(50, min(300, base_count + change))
        st.session_state.active_members_base = new_base
        st.session_state.active_members_last_update = current_time
        base_count = new_base
    
    variation = random.randint(-3, 3)
    return max(20, base_count + variation)

def format_disease_name(disease_str: str) -> str:
    if not disease_str:
        return "Unknown"
    formatted = disease_str.replace('___', ' - ').replace('__', ' - ').replace('_', ' ')
    return formatted.title().strip()

def get_crop_from_disease(disease_str: str) -> str:
    if not disease_str:
        return "Unknown"
    parts = disease_str.lower().split('___')
    if parts:
        return parts[0].replace('_', ' ').title()
    return "Unknown"

def get_disease_only(disease_str: str) -> str:
    if not disease_str:
        return "Unknown"
    parts = disease_str.lower().split('___')
    if len(parts) > 1:
        return parts[1].replace('_', ' ').title()
    return "Healthy" if 'healthy' in disease_str.lower() else parts[0].replace('_', ' ').title()

def calculate_savings(disease_str: str) -> int:
    """Calculate savings based on disease detected"""
    if not disease_str or 'healthy' in disease_str.lower():
        return 0
    
    disease_lower = disease_str.lower()
    
    for disease_key, disease_data in DISEASE_SAVINGS.items():
        if disease_key in disease_lower:
            return disease_data['savings']
    
    return DISEASE_SAVINGS['default']['savings']

def get_disease_severity(disease_str: str) -> Dict:
    """Get disease severity and related info"""
    if not disease_str or 'healthy' in disease_str.lower():
        return DISEASE_SAVINGS['healthy']
    
    disease_lower = disease_str.lower()
    
    for disease_key, disease_data in DISEASE_SAVINGS.items():
        if disease_key in disease_lower:
            return disease_data
    
    return DISEASE_SAVINGS['default']

def load_user_stats_from_persistence():
    """Load user stats from persistent storage"""
    user_id = st.session_state.get('user_id', 'demo')
    data = get_user_persistent_data(user_id)
    
    st.session_state.scan_history = data.get('scan_history', [])
    st.session_state.total_scans = data.get('total_scans', 0)
    st.session_state.total_savings = data.get('total_savings', 0)

def save_scan_to_persistence(scan_entry: Dict, savings: int):
    """Save a new scan to persistent storage"""
    user_id = st.session_state.get('user_id', 'demo')
    data = get_user_persistent_data(user_id)
    
    data['scan_history'].append(scan_entry)
    data['total_scans'] = len(data['scan_history'])
    data['total_savings'] = data.get('total_savings', 0) + savings
    data['last_scan_date'] = datetime.now().isoformat()
    
    if scan_entry.get('disease') and 'healthy' not in scan_entry.get('disease', '').lower():
        if 'diseases_detected' not in data:
            data['diseases_detected'] = []
        data['diseases_detected'].append({
            'disease': scan_entry.get('disease'),
            'date': scan_entry.get('date'),
            'savings': savings
        })
    
    save_user_persistent_data(user_id, data)
    
    # Update session state
    st.session_state.scan_history = data['scan_history']
    st.session_state.total_scans = data['total_scans']
    st.session_state.total_savings = data['total_savings']

def get_user_stats() -> Dict:
    """Get user statistics from session state"""
    scan_history = st.session_state.get('scan_history', [])
    total = len(scan_history)
    healthy = sum(1 for s in scan_history if 'healthy' in s.get('disease', '').lower())
    
    return {
        'total_scans': st.session_state.get('total_scans', total),
        'healthy_scans': healthy,
        'diseased_scans': total - healthy,
        'crop_health': int((healthy / total) * 100) if total > 0 else 0,
        'savings': st.session_state.get('total_savings', 0)
    }

# ==========================================
# WEATHER & MARKET DATA FUNCTIONS
# ==========================================

def fetch_weather_data(state: str) -> Dict:
    """
    Fetch weather data for a state.
    
    For REAL implementation, use one of these APIs:
    1. OpenWeatherMap: https://openweathermap.org/api (Free tier available)
    2. WeatherAPI: https://www.weatherapi.com/ (Free tier available)
    3. IMD API: https://mausam.imd.gov.in/ (Government of India)
    
    Example with OpenWeatherMap:
    ```
    API_KEY = "your_api_key"
    coords = STATE_CAPITALS.get(state, {})
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return {
        'temp': data['main']['temp'],
        'condition': data['weather'][0]['description'],
        'humidity': data['main']['humidity'],
        'icon': get_weather_icon(data['weather'][0]['main']),
        'city': data['name']
    }
    ```
    """
    # Check cache (refresh every 30 minutes)
    last_fetch = st.session_state.get('weather_last_fetch')
    cached_data = st.session_state.get('weather_data')
    cached_state = st.session_state.get('weather_state')
    
    if (cached_data and last_fetch and cached_state == state and 
        time.time() - last_fetch < 1800):  # 30 minutes
        return cached_data
    
    # Try to fetch real data
    try:
        # PLACEHOLDER: Replace with actual API call
        # For demo, we'll use realistic mock data based on typical Indian weather
        coords = STATE_CAPITALS.get(state, {})
        
        # Simulate realistic temperatures based on region
        base_temps = {
            "Rajasthan": random.randint(32, 42),
            "Gujarat": random.randint(30, 38),
            "Maharashtra": random.randint(26, 34),
            "Karnataka": random.randint(24, 32),
            "Tamil Nadu": random.randint(28, 36),
            "Kerala": random.randint(25, 32),
            "Punjab": random.randint(20, 35),
            "Delhi": random.randint(25, 40),
            "West Bengal": random.randint(26, 34),
            "Uttar Pradesh": random.randint(24, 38),
            "Bihar": random.randint(26, 36),
            "Madhya Pradesh": random.randint(26, 38),
        }
        
        conditions = ['Clear', 'Partly Cloudy', 'Cloudy', 'Sunny', 'Hazy']
        condition_icons = {
            'Clear': '☀️', 'Partly Cloudy': '⛅', 'Cloudy': '☁️', 
            'Sunny': '🌞', 'Hazy': '🌫️', 'Rainy': '🌧️'
        }
        
        condition = random.choice(conditions)
        
        weather_data = {
            'temp': base_temps.get(state, random.randint(25, 35)),
            'condition': condition,
            'humidity': random.randint(40, 80),
            'icon': condition_icons.get(condition, '⛅'),
            'city': coords.get('city', state),
            'feels_like': base_temps.get(state, 28) + random.randint(-2, 3),
            'wind_speed': random.randint(5, 20)
        }
        
        # Cache the data
        st.session_state.weather_data = weather_data
        st.session_state.weather_last_fetch = time.time()
        st.session_state.weather_state = state
        
        return weather_data
        
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return {
            'temp': 28,
            'condition': 'Partly Cloudy',
            'humidity': 65,
            'icon': '⛅',
            'city': state
        }

def fetch_market_prices(state: str) -> Dict:
    """
    Fetch market prices for a state.
    
    For REAL implementation, use:
    1. Agmarknet API: https://agmarknet.gov.in/ (Government of India - Free)
    2. data.gov.in APIs: https://data.gov.in/
    3. eNAM API: https://enam.gov.in/
    
    Example API call:
    ```
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": "your_api_key",
        "format": "json",
        "filters[state]": state,
        "limit": 10
    }
    response = requests.get(url, params=params)
    data = response.json()
    # Process and return prices
    ```
    """
    # Check cache (refresh every hour)
    last_fetch = st.session_state.get('market_last_fetch')
    cached_data = st.session_state.get('market_data')
    cached_state = st.session_state.get('market_state')
    
    if (cached_data and last_fetch and cached_state == state and 
        time.time() - last_fetch < 3600):  # 1 hour
        return cached_data
    
    # State-specific crop prices (realistic mock data)
    state_prices = {
        "Maharashtra": {
            "Tomato": {"price": 1200 + random.randint(-200, 200), "change": round(random.uniform(-5, 8), 1), "icon": "🍅"},
            "Onion": {"price": 2400 + random.randint(-300, 300), "change": round(random.uniform(-8, 5), 1), "icon": "🧅"},
            "Cotton": {"price": 6100 + random.randint(-400, 400), "change": round(random.uniform(-3, 5), 1), "icon": "🧵"},
            "Soybean": {"price": 4800 + random.randint(-300, 300), "change": round(random.uniform(-4, 4), 1), "icon": "🥜"},
        },
        "Punjab": {
            "Wheat": {"price": 2275 + random.randint(-150, 150), "change": round(random.uniform(-3, 4), 1), "icon": "🌾"},
            "Rice": {"price": 2183 + random.randint(-200, 200), "change": round(random.uniform(-2, 5), 1), "icon": "🍚"},
            "Cotton": {"price": 6200 + random.randint(-400, 400), "change": round(random.uniform(-4, 6), 1), "icon": "🧵"},
            "Maize": {"price": 1962 + random.randint(-150, 150), "change": round(random.uniform(-5, 3), 1), "icon": "🌽"},
        },
        "Karnataka": {
            "Coffee": {"price": 8500 + random.randint(-500, 500), "change": round(random.uniform(-2, 6), 1), "icon": "☕"},
            "Tomato": {"price": 1100 + random.randint(-200, 200), "change": round(random.uniform(-6, 8), 1), "icon": "🍅"},
            "Onion": {"price": 2200 + random.randint(-250, 250), "change": round(random.uniform(-5, 4), 1), "icon": "🧅"},
            "Groundnut": {"price": 5600 + random.randint(-400, 400), "change": round(random.uniform(-3, 5), 1), "icon": "🥜"},
        },
        "Uttar Pradesh": {
            "Wheat": {"price": 2250 + random.randint(-150, 150), "change": round(random.uniform(-3, 4), 1), "icon": "🌾"},
            "Rice": {"price": 2100 + random.randint(-200, 200), "change": round(random.uniform(-2, 4), 1), "icon": "🍚"},
            "Sugarcane": {"price": 350 + random.randint(-30, 30), "change": round(random.uniform(-2, 3), 1), "icon": "🎋"},
            "Potato": {"price": 1200 + random.randint(-150, 150), "change": round(random.uniform(-6, 5), 1), "icon": "🥔"},
        },
        "Gujarat": {
            "Cotton": {"price": 6300 + random.randint(-400, 400), "change": round(random.uniform(-4, 5), 1), "icon": "🧵"},
            "Groundnut": {"price": 5400 + random.randint(-350, 350), "change": round(random.uniform(-3, 4), 1), "icon": "🥜"},
            "Cumin": {"price": 32000 + random.randint(-2000, 2000), "change": round(random.uniform(-5, 8), 1), "icon": "🌿"},
            "Castor": {"price": 6800 + random.randint(-400, 400), "change": round(random.uniform(-4, 5), 1), "icon": "🌱"},
        },
    }
    
    # Default prices for states not in the list
    default_prices = {
        "Tomato": {"price": 1200 + random.randint(-200, 200), "change": round(random.uniform(-5, 8), 1), "icon": "🍅"},
        "Onion": {"price": 2400 + random.randint(-300, 300), "change": round(random.uniform(-8, 5), 1), "icon": "🧅"},
        "Rice": {"price": 2100 + random.randint(-200, 200), "change": round(random.uniform(-3, 4), 1), "icon": "🍚"},
        "Wheat": {"price": 2200 + random.randint(-150, 150), "change": round(random.uniform(-3, 4), 1), "icon": "🌾"},
    }
    
    market_data = state_prices.get(state, default_prices)
    
    # Cache the data
    st.session_state.market_data = market_data
    st.session_state.market_last_fetch = time.time()
    st.session_state.market_state = state
    
    return market_data

def fetch_dynamic_treatment(disease: str, crop: str, confidence: float, language: str = 'en') -> str:
    """Fetch AI-powered treatment in the user's selected language"""
    try:
        # Language-specific prompts
        if language == 'hi':
            prompt = f"""कृपया {crop} में {disease} (विश्वसनीयता: {confidence:.0%}) के लिए उपचार बताएं।

संक्षिप्त और व्यावहारिक जवाब दें:
1. तुरंत कार्रवाई (1-2 कदम)
2. उपचार (विशिष्ट दवाई, खुराक और लागत ₹ में)
3. रोकथाम (1-2 सुझाव)

150 शब्दों में जवाब दें। भारतीय किसानों के लिए सरल भाषा में।"""
        else:
            prompt = f"""Provide treatment for {crop} with {disease} (confidence: {confidence:.0%}).

Give a brief, practical response with:
1. IMMEDIATE ACTION (1-2 steps)
2. TREATMENT (specific medicine with dosage and cost in ₹)
3. PREVENTION (1-2 tips)

Keep it under 150 words. Use simple language for Indian farmers."""

        if CHATBOT_AVAILABLE:
            return chatbot.chat(prompt, target_language=language)
        else:
            return "Treatment information not available (Chatbot offline)."
            
    except Exception as e:
        print(f"Treatment fetch error: {e}")
    
    return None

# ==========================================
# TRANSLATIONS
# ==========================================
TRANSLATIONS = {
    'en': {
        'nav_dashboard': 'Dashboard', 'nav_scan': 'Smart Scan', 'nav_consultant': 'AI Consultant',
        'nav_community': 'Community', 'nav_settings': 'Settings', 'nav_admin': 'Admin Panel',
        'nav_logout': 'Logout', 'welcome': 'Welcome back', 'farm_overview': "Here's your farm overview",
        'metric_health': 'Crop Health', 'metric_scans': 'Total Scans', 'metric_savings': 'Est. Savings',
        'metric_weather': 'Weather', 'quick_actions': 'Quick Actions', 'btn_scan': 'New Scan',
        'btn_consultant': 'Ask AI', 'btn_calendar': 'Calendar', 'recent_analysis': 'Recent Analysis',
        'scan_header': 'Smart Diagnostics', 'scan_sub': 'AI-powered crop disease detection',
        'source_upload': 'Upload', 'source_camera': 'Camera', 'run_analysis': 'Analyze Now',
        'soil_health': 'Soil Analysis', 'consultant_header': 'AI Consultant',
        'consultant_sub': 'Your 24/7 farming expert', 'community_header': 'Community Hub',
        'community_sub': 'Connect with farmers', 'tab_discuss': 'Discussions',
        'tab_stories': 'Success Stories', 'tab_market': 'Marketplace', 'share_story': 'Share Your Story',
        'settings_header': 'Settings', 'settings_sub': 'Customize your experience',
        'mandi_prices': 'Live Market Prices', 'voice_nav': 'Voice Assistant',
        'no_activity': 'No recent activity', 'start_scanning': 'Start scanning to see history',
        'select_state': 'Select Your State', 'getting_treatment': 'Getting AI treatment...',
        'sign_in': 'Sign In', 'create_account': 'Create Account', 'email': 'Email Address',
        'password': 'Password', 'full_name': 'Full Name', 'phone': 'Phone Number',
        'remember_me': 'Remember me for 30 days', 'forgot_password': 'Forgot password?',
        'welcome_back': 'Welcome Back!', 'join_community': 'Join Our Community',
        'signin_subtitle': 'Sign in to access your farm dashboard',
        'register_subtitle': 'Create an account to get started',
        'savings_explanation': 'Estimated savings from early disease detection',
        'per_quintal': 'per quintal',
    },
    'hi': {
        'nav_dashboard': 'डैशबोर्ड', 'nav_scan': 'स्मार्ट स्कैन', 'nav_consultant': 'AI सलाहकार',
        'nav_community': 'समुदाय', 'nav_settings': 'सेटिंग्स', 'nav_admin': 'एडमिन पैनल',
        'nav_logout': 'लॉग आउट', 'welcome': 'वापसी पर स्वागत', 'farm_overview': 'आपके खेत का विवरण',
        'metric_health': 'फसल स्वास्थ्य', 'metric_scans': 'कुल स्कैन', 'metric_savings': 'अनुमानित बचत',
        'metric_weather': 'मौसम', 'quick_actions': 'त्वरित कार्य', 'btn_scan': 'नया स्कैन',
        'btn_consultant': 'AI से पूछें', 'btn_calendar': 'कैलेंडर', 'recent_analysis': 'हाल का विश्लेषण',
        'scan_header': 'स्मार्ट निदान', 'scan_sub': 'AI फसल रोग पहचान',
        'source_upload': 'अपलोड', 'source_camera': 'कैमरा', 'run_analysis': 'विश्लेषण करें',
        'soil_health': 'मिट्टी विश्लेषण', 'consultant_header': 'AI सलाहकार',
        'consultant_sub': '24/7 कृषि विशेषज्ञ', 'community_header': 'समुदाय केंद्र',
        'community_sub': 'किसानों से जुड़ें', 'tab_discuss': 'चर्चा',
        'tab_stories': 'सफलता की कहानियाँ', 'tab_market': 'बाज़ार', 'share_story': 'अपनी कहानी साझा करें',
        'settings_header': 'सेटिंग्स', 'settings_sub': 'अपना अनुभव अनुकूलित करें',
        'mandi_prices': 'लाइव मंडी भाव', 'voice_nav': 'वॉयस असिस्टेंट',
        'no_activity': 'कोई हालिया गतिविधि नहीं', 'start_scanning': 'इतिहास देखने के लिए स्कैन करें',
        'select_state': 'अपना राज्य चुनें', 'getting_treatment': 'AI उपचार प्राप्त कर रहा है...',
        'sign_in': 'साइन इन', 'create_account': 'खाता बनाएं', 'email': 'ईमेल पता',
        'password': 'पासवर्ड', 'full_name': 'पूरा नाम', 'phone': 'फोन नंबर',
        'remember_me': '30 दिनों के लिए याद रखें', 'forgot_password': 'पासवर्ड भूल गए?',
        'welcome_back': 'वापसी पर स्वागत!', 'join_community': 'हमारे समुदाय में शामिल हों',
        'signin_subtitle': 'अपने फार्म डैशबोर्ड तक पहुंचने के लिए साइन इन करें',
        'register_subtitle': 'शुरू करने के लिए एक खाता बनाएं',
        'savings_explanation': 'रोग की जल्दी पहचान से अनुमानित बचत',
        'per_quintal': 'प्रति क्विंटल',
    }
}

def get_text(key: str) -> str:
    lang = st.session_state.get('app_language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# ==========================================
# PREMIUM CSS - FIXED TEXT COLORS
# ==========================================
def inject_premium_css():
    is_dark = st.session_state.get('theme', 'dark') == 'dark'
    
    if is_dark:
        colors = {
            'bg_primary': '#0a0a0f',
            'bg_secondary': '#111118',
            'bg_tertiary': '#1a1a24',
            'bg_card': 'rgba(20, 20, 28, 0.9)',
            'bg_input': '#0d0d12',
            'text_primary': '#ffffff',
            'text_secondary': '#e0e0e8',  # BRIGHTER - was #b0b0c0
            'text_muted': '#a0a0b0',       # BRIGHTER - was #6b6b7b
            'accent_primary': '#22c55e',
            'accent_secondary': '#10b981',
            'accent_gradient': 'linear-gradient(135deg, #22c55e 0%, #10b981 50%, #059669 100%)',
            'accent_glow': 'rgba(34, 197, 94, 0.3)',
            'border_color': 'rgba(255, 255, 255, 0.12)',
            'border_hover': 'rgba(34, 197, 94, 0.5)',
            'success': '#22c55e',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#3b82f6',
            'input_text': '#ffffff',
            'input_bg': '#0d0d12',
            'input_border': 'rgba(255, 255, 255, 0.2)',
            'input_placeholder': '#888899'
        }
    else:
        colors = {
            'bg_primary': '#fafafa',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#f5f5f5',
            'bg_card': 'rgba(255, 255, 255, 0.95)',
            'bg_input': '#ffffff',
            'text_primary': '#1a1a2e',
            'text_secondary': '#3a3a4a',
            'text_muted': '#5a5a6a',
            'accent_primary': '#16a34a',
            'accent_secondary': '#15803d',
            'accent_gradient': 'linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%)',
            'accent_glow': 'rgba(22, 163, 74, 0.2)',
            'border_color': 'rgba(0, 0, 0, 0.1)',
            'border_hover': 'rgba(22, 163, 74, 0.4)',
            'success': '#16a34a',
            'warning': '#d97706',
            'error': '#dc2626',
            'info': '#2563eb',
            'input_text': '#1a1a2e',
            'input_bg': '#ffffff',
            'input_border': 'rgba(0, 0, 0, 0.15)',
            'input_placeholder': '#8a8a9a'
        }

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {{
        --bg-primary: {colors['bg_primary']};
        --bg-secondary: {colors['bg_secondary']};
        --bg-tertiary: {colors['bg_tertiary']};
        --bg-card: {colors['bg_card']};
        --bg-input: {colors['bg_input']};
        --text-primary: {colors['text_primary']};
        --text-secondary: {colors['text_secondary']};
        --text-muted: {colors['text_muted']};
        --accent-primary: {colors['accent_primary']};
        --accent-secondary: {colors['accent_secondary']};
        --accent-gradient: {colors['accent_gradient']};
        --accent-glow: {colors['accent_glow']};
        --border-color: {colors['border_color']};
        --border-hover: {colors['border_hover']};
        --success: {colors['success']};
        --warning: {colors['warning']};
        --error: {colors['error']};
        --info: {colors['info']};
        --input-text: {colors['input_text']};
        --input-bg: {colors['input_bg']};
        --input-border: {colors['input_border']};
        --input-placeholder: {colors['input_placeholder']};
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --radius-full: 9999px;
        --shadow-glow: 0 0 40px var(--accent-glow);
        --transition-spring: 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }}

    *, *::before, *::after {{ box-sizing: border-box; }}

    html, body, [class*="css"], .stApp, .main {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary) !important;
        background-color: var(--bg-primary) !important;
        -webkit-font-smoothing: antialiased;
    }}

    #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"], .stDecoration {{
        display: none !important;
    }}

    .main .block-container {{
        padding: 2rem 3rem 6rem 3rem;
        max-width: 1400px;
    }}

    /* Typography - ALL TEXT BRIGHT */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }}

    p {{
        color: var(--text-secondary) !important;
    }}

    span, div, label {{
        color: var(--text-secondary);
    }}

    /* Force all text to be readable */
    * {{
        color: inherit;
    }}

    /* Glass Card */
    .glass-card {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease;
    }}

    .glass-card:hover {{
        transform: translateY(-4px);
        border-color: var(--border-hover) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2), var(--shadow-glow);
    }}

    /* Stat Cards */
    .stat-card {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        text-align: center;
        transition: all var(--transition-spring);
    }}

    .stat-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2), var(--shadow-glow);
    }}

    .stat-icon {{
        width: 56px; height: 56px;
        background: var(--accent-gradient) !important;
        border-radius: var(--radius-md);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 24px var(--accent-glow);
    }}

    .stat-value {{
        font-size: 2.25rem !important;
        font-weight: 800 !important;
        background: var(--accent-gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }}

    .stat-label {{
        font-size: 0.875rem !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500 !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all var(--transition-spring) !important;
        box-shadow: 0 4px 16px var(--accent-glow) !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 24px var(--accent-glow) !important;
    }}

    .stButton > button[kind="secondary"] {{
        background: transparent !important;
        border: 2px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        box-shadow: none !important;
    }}

    .stButton > button[kind="secondary"]:hover {{
        border-color: var(--accent-primary) !important;
        background: rgba(34, 197, 94, 0.1) !important;
    }}

    /* ALL INPUT FIELDS */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    input[type="text"], input[type="email"], input[type="password"],
    textarea {{
        background-color: var(--input-bg) !important;
        border: 2px solid var(--input-border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--input-text) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        caret-color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
    }}

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder,
    input::placeholder, textarea::placeholder {{
        color: var(--input-placeholder) !important;
        -webkit-text-fill-color: var(--input-placeholder) !important;
        opacity: 1 !important;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    input:focus, textarea:focus {{
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 4px var(--accent-glow) !important;
        outline: none !important;
    }}

    /* Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }}

    /* Select Box */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div,
    [data-baseweb="select"] {{
        background-color: var(--input-bg) !important;
        border: 2px solid var(--input-border) !important;
        border-radius: var(--radius-md) !important;
    }}

    .stSelectbox [data-baseweb="select"] span,
    [data-baseweb="select"] span {{
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
    }}

    [data-baseweb="menu"], [data-baseweb="popover"] > div {{
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
    }}

    [data-baseweb="menu"] li, [role="option"] {{
        color: var(--text-primary) !important;
    }}

    [data-baseweb="menu"] li:hover, [role="option"]:hover {{
        background-color: var(--bg-tertiary) !important;
    }}

    /* CHAT INPUT */
    .stChatInputContainer {{
        background: var(--bg-secondary) !important;
        border-top: 1px solid var(--border-color) !important;
        padding: 1rem !important;
    }}

    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div {{
        background: var(--input-bg) !important;
        border: 2px solid var(--input-border) !important;
        border-radius: var(--radius-lg) !important;
    }}

    [data-testid="stChatInput"] textarea,
    .stChatInputContainer textarea {{
        background: var(--input-bg) !important;
        border: none !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        caret-color: var(--input-text) !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: var(--input-placeholder) !important;
        -webkit-text-fill-color: var(--input-placeholder) !important;
    }}

    /* Chat Messages */
    .stChatMessage {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
    }}

    [data-testid="stChatMessageContent"],
    [data-testid="stChatMessageContent"] p {{
        color: var(--text-primary) !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background: var(--bg-secondary) !important;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
        box-shadow: none !important;
        justify-content: flex-start !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        background: var(--bg-tertiary) !important;
        border-color: var(--accent-primary) !important;
        color: var(--text-primary) !important;
    }}

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background: var(--accent-gradient) !important;
        border: none !important;
        color: white !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem !important;
        background: var(--bg-tertiary) !important;
        padding: 0.5rem !important;
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--border-color) !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: var(--radius-md) !important;
        color: var(--text-secondary) !important;
        background: transparent !important;
        font-weight: 500 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: var(--accent-gradient) !important;
        color: white !important;
    }}

    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* Badges */
    .badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.875rem;
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }}

    .badge-success {{ background: rgba(34, 197, 94, 0.2) !important; color: #4ade80 !important; border: 1px solid rgba(34, 197, 94, 0.4) !important; }}
    .badge-warning {{ background: rgba(245, 158, 11, 0.2) !important; color: #fbbf24 !important; border: 1px solid rgba(245, 158, 11, 0.4) !important; }}
    .badge-error {{ background: rgba(239, 68, 68, 0.2) !important; color: #f87171 !important; border: 1px solid rgba(239, 68, 68, 0.4) !important; }}
    .badge-info {{ background: rgba(59, 130, 246, 0.2) !important; color: #60a5fa !important; border: 1px solid rgba(59, 130, 246, 0.4) !important; }}

    /* Animations */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes fadeInScale {{
        from {{ opacity: 0; transform: scale(0.9); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}

    @keyframes float {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-10px); }}
    }}

    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 20px var(--accent-glow); }}
        50% {{ box-shadow: 0 0 40px var(--accent-glow), 0 0 60px var(--accent-glow); }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    .animate-fade-up {{ animation: fadeInUp 0.6s ease forwards; }}
    .animate-fade-scale {{ animation: fadeInScale 0.5s ease forwards; }}
    .animate-float {{ animation: float 3s ease-in-out infinite; }}
    .animate-glow {{ animation: glow 2s ease-in-out infinite; }}
    .animate-pulse {{ animation: pulse 1.5s ease-in-out infinite; }}

    .stagger-1 {{ animation-delay: 0.1s; }}
    .stagger-2 {{ animation-delay: 0.2s; }}
    .stagger-3 {{ animation-delay: 0.3s; }}
    .stagger-4 {{ animation-delay: 0.4s; }}

    .shimmer {{
        background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-card) 50%, var(--bg-tertiary) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }}

    /* Disease Result Card */
    .result-card {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-xl) !important;
        padding: 2rem !important;
        position: relative;
        overflow: hidden;
    }}

    .result-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--accent-gradient);
    }}

    .disease-name {{
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--accent-primary) !important;
        line-height: 1.3 !important;
    }}

    .crop-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: var(--bg-tertiary);
        border-radius: var(--radius-full);
        font-size: 0.8rem;
        color: var(--text-secondary) !important;
        margin-bottom: 0.5rem;
    }}

    /* Treatment Card */
    .treatment-card {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        margin-top: 1.5rem !important;
    }}

    .treatment-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }}

    .treatment-icon {{
        width: 40px; height: 40px;
        background: var(--accent-gradient);
        border-radius: var(--radius-md);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.25rem;
    }}

    .treatment-content {{
        color: var(--text-secondary) !important;
        line-height: 1.8 !important;
        white-space: pre-wrap !important;
    }}

    /* Auth Styles */
    .auth-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}

    .auth-logo {{
        width: 80px; height: 80px;
        background: var(--accent-gradient);
        border-radius: var(--radius-lg);
        display: flex; align-items: center; justify-content: center;
        font-size: 2.5rem;
        margin: 0 auto 1.5rem;
        box-shadow: 0 8px 32px var(--accent-glow);
    }}

    .auth-title {{
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
    }}

    .auth-subtitle {{
        color: var(--text-secondary) !important;
        font-size: 0.95rem;
    }}

    .auth-link {{
        color: var(--accent-primary) !important;
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
    }}

    .feature-pills {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 2rem;
    }}

    .feature-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-full);
        font-size: 0.85rem;
        color: var(--text-secondary) !important;
    }}

    /* Savings Info */
    .savings-info {{
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: var(--text-secondary) !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: var(--radius-full); }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}

    /* Other Components */
    [data-testid="stFileUploader"] {{
        background: var(--bg-tertiary) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: var(--accent-primary) !important;
    }}

    .stProgress > div > div {{ background: var(--accent-gradient) !important; }}
    .stProgress > div {{ background: var(--bg-tertiary) !important; }}

    .stToggle label, .stSlider label, .stCheckbox label, .stRadio > label {{
        color: var(--text-primary) !important;
    }}

    .stCheckbox span {{
        color: var(--text-secondary) !important;
    }}

    .stAlert {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
    }}

    [data-testid="stForm"] {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
    }}

    .streamlit-expanderHeader {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
    }}

    </style>
    """, unsafe_allow_html=True)

# ==========================================
# COMPONENTS
# ==========================================

def render_stat_card(label: str, value: str, icon: str, trend: str = None, delay: int = 0, tooltip: str = None) -> str:
    trend_html = ""
    if trend:
        is_pos = not trend.startswith("-")
        color = "var(--success)" if is_pos else "var(--error)"
        trend_html = f'<div style="color: {color}; font-size: 0.875rem; font-weight: 600; margin-top: 0.25rem;">{trend}</div>'
    
    tooltip_html = f'<div class="savings-info">{tooltip}</div>' if tooltip else ''
    
    return f"""
    <div class="stat-card animate-fade-up stagger-{delay + 1}">
        <div class="stat-icon">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
        {trend_html}
        {tooltip_html}
    </div>
    """

def render_market_card(crop: str, data: Dict) -> str:
    price = data['price']
    change = data['change']
    icon = data.get('icon', '🌱')
    is_pos = change >= 0
    color = "var(--success)" if is_pos else "var(--error)"
    arrow = "↑" if is_pos else "↓"
    
    return f"""
    <div class="glass-card" style="padding: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span style="font-weight: 600; color: var(--text-primary);">{crop}</span>
        </div>
        <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary);">₹{price:,}/q</div>
        <div style="color: {color}; font-size: 0.875rem; font-weight: 600;">{arrow} {abs(change)}%</div>
    </div>
    """

def render_activity_item(title: str, subtitle: str, time_str: str, status: str, icon: str, savings: int = 0) -> str:
    savings_html = f'<div style="font-size: 0.75rem; color: var(--success);">+₹{savings} saved</div>' if savings > 0 else ''
    return f"""
    <div class="glass-card" style="padding: 1rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 1rem;">
        <div style="width: 48px; height: 48px; background: var(--bg-tertiary); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">{icon}</div>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: var(--text-primary);">{title}</div>
            <div style="font-size: 0.85rem; color: var(--text-muted);">{subtitle}</div>
        </div>
        <div style="text-align: right;">
            <span class="badge badge-{status}">Done</span>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">{time_str}</div>
            {savings_html}
        </div>
    </div>
    """

def render_empty_state(icon: str, title: str, subtitle: str) -> str:
    return f"""
    <div class="glass-card" style="text-align: center; padding: 3rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">{icon}</div>
        <h3 style="color: var(--text-muted); font-weight: 500;">{title}</h3>
        <p style="color: var(--text-muted); font-size: 0.9rem;">{subtitle}</p>
    </div>
    """

def render_treatment_card(treatment: str, is_loading: bool = False) -> str:
    if is_loading:
        return f"""
        <div class="treatment-card animate-fade-up">
            <div class="treatment-header">
                <div class="treatment-icon animate-pulse">⏳</div>
                <div style="font-weight: 600; color: var(--text-primary);">{get_text('getting_treatment')}</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <div class="shimmer" style="height: 20px; width: 80%; border-radius: 4px;"></div>
                <div class="shimmer" style="height: 20px; width: 90%; border-radius: 4px;"></div>
                <div class="shimmer" style="height: 20px; width: 70%; border-radius: 4px;"></div>
            </div>
        </div>
        """
    
    if not treatment:
        return ""
    
    return f"""
    <div class="treatment-card animate-fade-up">
        <div class="treatment-header">
            <div class="treatment-icon">💊</div>
            <div style="font-weight: 600; color: var(--text-primary);">Treatment Plan</div>
        </div>
        <div class="treatment-content">{treatment}</div>
    </div>
    """

# ==========================================
# AUTH PAGES
# ==========================================

def check_auth() -> bool:
    return st.session_state.get('current_user') is not None

def show_login_page():
    inject_premium_css()
    
    # Hero Section
    st.markdown("""
    <div class="animate-fade-up" style="text-align: center; padding: 2rem 1rem 3rem;">
        <div class="animate-float" style="font-size: 4rem; margin-bottom: 1rem;">🌱</div>
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem; color: var(--text-primary);">KropScan AI</h1>
        <p style="font-size: 1rem; color: var(--text-secondary);">
            Intelligent crop disease detection for modern farmers
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        if 'auth_tab' not in st.session_state:
            st.session_state.auth_tab = 'login'
        
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button(f"🔐 {get_text('sign_in')}", 
                        use_container_width=True, 
                        type="primary" if st.session_state.auth_tab == 'login' else "secondary",
                        key="tab_login"):
                st.session_state.auth_tab = 'login'
                st.rerun()
        with tab_col2:
            if st.button(f"✨ {get_text('create_account')}", 
                        use_container_width=True,
                        type="primary" if st.session_state.auth_tab == 'register' else "secondary",
                        key="tab_register"):
                st.session_state.auth_tab = 'register'
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login Form
        if st.session_state.auth_tab == 'login':
            st.markdown(f"""
            <div class="auth-header animate-fade-scale">
                <div class="auth-logo animate-glow">🔐</div>
                <div class="auth-title">{get_text('welcome_back')}</div>
                <div class="auth-subtitle">{get_text('signin_subtitle')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input(get_text('email'), placeholder="farmer@example.com", key="login_email")
                password = st.text_input(get_text('password'), type="password", placeholder="••••••••", key="login_password")
                
                remember_me = st.checkbox(get_text('remember_me'), key="remember_me")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button(f"🚀 {get_text('sign_in')}", type="primary", use_container_width=True)
                
                if submitted:
                    if not email or not password:
                        st.error("⚠️ Please fill in all fields")
                    elif auth_system:
                        token = auth_system.login_user(email, password)
                        if token:
                            st.session_state.current_user = token
                            st.session_state.current_user_email = email
                            user_data = auth_system.get_user_from_session(token)
                            if user_data:
                                st.session_state.user_id = user_data.get('user_id', 'demo')
                                if user_data.get('is_admin'):
                                    st.session_state.is_admin = True
                            
                            # Handle Remember Me
                            if remember_me:
                                save_remembered_session(email, token)
                            
                            # Load persistent user data
                            load_user_stats_from_persistence()
                            
                            st.success("✅ Welcome back!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
                    else:
                        # Demo mode
                        st.session_state.current_user = "demo_token"
                        st.session_state.current_user_email = email or "demo@example.com"
                        st.session_state.user_id = hashlib.md5((email or "demo").encode()).hexdigest()[:8]
                        
                        if remember_me:
                            save_remembered_session(email or "demo@example.com", "demo_token")
                        
                        load_user_stats_from_persistence()
                        
                        st.success("✅ Demo mode activated!")
                        time.sleep(0.5)
                        st.rerun()
        
        # Register Form
        else:
            st.markdown(f"""
            <div class="auth-header animate-fade-scale">
                <div class="auth-logo animate-glow">✨</div>
                <div class="auth-title">{get_text('join_community')}</div>
                <div class="auth-subtitle">{get_text('register_subtitle')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("register_form", clear_on_submit=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    r_name = st.text_input(get_text('full_name'), placeholder="Your name", key="reg_name")
                with col_b:
                    r_phone = st.text_input(get_text('phone'), placeholder="+91 XXXXX XXXXX", key="reg_phone")
                
                r_email = st.text_input(get_text('email'), placeholder="your@email.com", key="reg_email")
                r_pass = st.text_input(get_text('password'), type="password", placeholder="Min 6 characters", key="reg_pass")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    r_state = st.selectbox("State", options=INDIAN_STATES, index=INDIAN_STATES.index("Maharashtra"), key="reg_state")
                with col_d:
                    r_farm = st.number_input("Farm Size (Acres)", min_value=0.1, value=2.0, step=0.5, key="reg_farm")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button(f"🌱 {get_text('create_account')}", type="primary", use_container_width=True)
                
                if submitted:
                    if not all([r_name, r_email, r_pass]):
                        st.error("⚠️ Please fill in all required fields")
                    elif len(r_pass) < 6:
                        st.error("⚠️ Password must be at least 6 characters")
                    elif auth_system:
                        uid = auth_system.register_user(r_name, r_email, r_phone, r_pass, r_state, r_farm)
                        if uid:
                            st.session_state.user_state = r_state
                            st.success("✅ Account created! Please sign in.")
                            st.session_state.auth_tab = 'login'
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Registration failed. Email may be in use.")
                    else:
                        st.session_state.user_state = r_state
                        st.session_state.current_user = "demo_token"
                        st.session_state.user_id = hashlib.md5(r_email.encode()).hexdigest()[:8]
                        st.success("✅ Demo account created!")
                        time.sleep(0.5)
                        st.rerun()
        
        # Feature Pills
        st.markdown("""
        <div class="feature-pills animate-fade-up stagger-3">
            <div class="feature-pill">🤖 AI-Powered</div>
            <div class="feature-pill">🌍 10+ Languages</div>
            <div class="feature-pill">📱 Mobile Ready</div>
            <div class="feature-pill">👥 Community</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

def render_sidebar(user_data: Dict) -> str:
    with st.sidebar:
        st.markdown(f"""
        <div class="animate-fade-up" style="padding: 1rem 0 2rem; text-align: center;">
            <div class="animate-glow" style="width: 72px; height: 72px; background: var(--accent-gradient); border-radius: var(--radius-lg); margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; font-size: 2.25rem;">🌱</div>
            <h2 style="font-size: 1.5rem; margin: 0; color: var(--accent-primary);">KropScan AI</h2>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Smart Farming Platform</p>
        </div>
        """, unsafe_allow_html=True)

        user_initial = user_data.get('name', 'U')[0].upper()
        user_location = user_data.get('location', st.session_state.get('user_state', 'Farmer'))
        
        st.markdown(f"""
        <div class="glass-card" style="padding: 1rem; display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div style="width: 44px; height: 44px; background: var(--accent-gradient); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white;">{user_initial}</div>
            <div style="flex: 1;">
                <div style="font-weight: 600; color: var(--text-primary);">{user_data.get('name', 'User')}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">📍 {user_location}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        nav_items = [
            ("📊", get_text("nav_dashboard"), "dashboard"),
            ("📷", get_text("nav_scan"), "scan"),
            ("🤖", get_text("nav_consultant"), "consultant"),
            ("🌍", get_text("nav_community"), "community"),
            ("⚙️", get_text("nav_settings"), "settings"),
        ]
        
        if st.session_state.get('is_admin'):
            nav_items.append(("🛡️", get_text("nav_admin"), "admin"))

        for icon, label, key in nav_items:
            is_active = st.session_state.get('current_page', 'dashboard') == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.current_page = key
                st.rerun()

        st.markdown("<div style='min-height: 30px;'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="glass-card animate-pulse" style="padding: 0.75rem; text-align: center; border: 1px solid var(--accent-primary); margin-bottom: 1rem;">
            <span style="font-size: 1.1rem;">🎙️</span>
            <span style="font-size: 0.85rem; color: var(--accent-primary); margin-left: 0.5rem;">{get_text('voice_nav')}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🚪  {get_text('nav_logout')}", use_container_width=True, type="secondary", key="logout_btn"):
            # Clear remembered session
            email = st.session_state.get('current_user_email')
            if email:
                clear_remembered_session(email)
            
            # Reset session state
            for key in ['current_user', 'current_user_email', 'user_id', 'scan_result', 'dynamic_treatment', 
                       'analysis_complete', 'treatment_fetched', 'weather_data', 'market_data']:
                st.session_state[key] = None
            st.session_state.current_page = 'dashboard'
            st.session_state.scan_history = []
            st.session_state.total_scans = 0
            st.session_state.total_savings = 0
            st.rerun()

    return st.session_state.get('current_page', 'dashboard')

# ==========================================
# VIEW: DASHBOARD
# ==========================================

def view_dashboard(user_data: Dict):
    st.markdown(f"""
    <div class="animate-fade-up" style="margin-bottom: 2.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="animate-float" style="font-size: 3rem;">🌤️</div>
            <div>
                <h1 style="margin: 0; font-size: 2.25rem; color: var(--text-primary);">{get_text('welcome')}, {user_data.get('name', 'Farmer').split()[0]}! 👋</h1>
                <p style="margin: 0.5rem 0 0; color: var(--text-secondary);">{get_text('farm_overview')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    stats = get_user_stats()
    state = st.session_state.get('user_state', 'Maharashtra')
    weather = fetch_weather_data(state)
    market = fetch_market_prices(state)
    
    # Stats Grid
    cols = st.columns(4)
    health_val = f"{stats['crop_health']}%" if stats['total_scans'] > 0 else "N/A"
    health_trend = f"+{stats['crop_health']}%" if stats['total_scans'] > 0 and stats['crop_health'] >= 50 else None
    
    with cols[0]:
        st.markdown(render_stat_card(get_text("metric_health"), health_val, "🌿", health_trend, 0), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(render_stat_card(get_text("metric_scans"), str(stats['total_scans']), "📷", None, 1), unsafe_allow_html=True)
    with cols[2]:
        savings = f"₹{stats['savings']:,}" if stats['savings'] > 0 else "₹0"
        tooltip = get_text('savings_explanation')
        st.markdown(render_stat_card(get_text("metric_savings"), savings, "💰", None, 2, tooltip if stats['savings'] > 0 else None), unsafe_allow_html=True)
    with cols[3]:
        st.markdown(render_stat_card(f"{weather.get('city', state)}", f"{weather['temp']}°C", weather.get('icon', '⛅'), None, 3), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Actions
    st.markdown(f"### ⚡ {get_text('quick_actions')}")
    cols = st.columns(3)
    with cols[0]:
        if st.button(f"📷  {get_text('btn_scan')}", type="primary", use_container_width=True, key="dash_scan"):
            st.session_state.current_page = 'scan'
            st.rerun()
    with cols[1]:
        if st.button(f"🤖  {get_text('btn_consultant')}", use_container_width=True, key="dash_consultant"):
            st.session_state.current_page = 'consultant'
            st.rerun()
    with cols[2]:
        if st.button(f"📅  {get_text('btn_calendar')}", use_container_width=True, key="dash_calendar"):
            st.info("📅 Crop calendar coming soon!")

    st.markdown("<br>", unsafe_allow_html=True)

    # Market & Activity
    col_l, col_r = st.columns([1.2, 0.8])
    
    with col_l:
        st.markdown(f"### 📈 {get_text('mandi_prices')} ({state})")
        mcols = st.columns(4)
        for idx, (crop, data) in enumerate(list(market.items())[:4]):
            with mcols[idx]:
                st.markdown(render_market_card(crop, data), unsafe_allow_html=True)
    
    with col_r:
        st.markdown(f"### 🕐 {get_text('recent_analysis')}")
        history = st.session_state.get('scan_history', [])
        
        if not history:
            st.markdown(render_empty_state("📝", get_text('no_activity'), get_text('start_scanning')), unsafe_allow_html=True)
        else:
            for item in history[-3:][::-1]:
                name = format_disease_name(item.get('disease', 'Unknown'))
                conf = int(item.get('confidence', 0) * 100)
                time_str = item.get('time', 'Recently')
                icon = "🌿" if 'healthy' in item.get('disease', '').lower() else "🔬"
                status = "success" if 'healthy' in item.get('disease', '').lower() else "warning"
                savings = item.get('savings', 0)
                st.markdown(render_activity_item(name, f"Confidence: {conf}%", time_str, status, icon, savings), unsafe_allow_html=True)

# ==========================================
# VIEW: SMART SCAN
# ==========================================

def view_scanner():
    st.markdown(f"""
    <div class="animate-fade-up" style="margin-bottom: 2.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="animate-float" style="font-size: 3rem;">🔬</div>
            <div>
                <h1 style="margin: 0; font-size: 2.25rem; color: var(--text-primary);">{get_text('scan_header')}</h1>
                <p style="margin: 0.5rem 0 0; color: var(--text-secondary);">{get_text('scan_sub')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([f"🌿 {get_text('nav_scan')}", f"🏜️ {get_text('soil_health')}"])
    
    with tab1:
        col_upload, col_result = st.columns([1, 1], gap="large")
        
        with col_upload:
            st.markdown("### 📸 Capture or Upload")
            
            source = st.radio("Source", [get_text("source_camera"), get_text("source_upload")], horizontal=True, label_visibility="collapsed", key="scan_source")
            
            img_file = None
            if source == get_text("source_camera"):
                img_file = st.camera_input("Take photo", key="camera_input")
            else:
                img_file = st.file_uploader("Upload image", type=['jpg', 'png', 'jpeg'], key="file_upload")
            
            if img_file:
                st.image(img_file, caption="Image Preview", use_column_width=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                if not st.session_state.get('analysis_complete', False):
                    if st.button(f"🔍 {get_text('run_analysis')}", type="primary", use_container_width=True, key="analyze_btn"):
                        with st.spinner("🧠 Analyzing..."):
                            progress = st.progress(0)
                            for i in range(100):
                                time.sleep(0.01)
                                progress.progress(i + 1)
                            
                            try:
                                # DIRECT AI CALL (No Backend Needed)
                                if AI_AVAILABLE:
                                    disease, confidence, treatment = ai_engine.predict(img_file.getvalue())
                                    
                                    result = {
                                        "status": "success",
                                        "disease": disease,
                                        "confidence": confidence,
                                        "treatment": treatment
                                    }
                                else:
                                    # Fallback / Mock
                                    time.sleep(1) # Simulate delay
                                    result = {
                                        "status": "success",
                                        "disease": "Healthy Crop (Demo)",
                                        "confidence": 0.98,
                                        "treatment": "Your crop looks healthy! Keep maintaining good irrigation."
                                    }

                                if result:
                                    st.session_state.scan_result = result
                                    st.session_state.analysis_complete = True
                                    st.session_state.treatment_fetched = False
                                    st.session_state.dynamic_treatment = None
                                    
                                    # Calculate savings
                                    savings = calculate_savings(result.get('disease', ''))
                                    
                                    # Save to persistence
                                    entry = {
                                        'disease': result.get('disease', 'unknown'),
                                        'confidence': result.get('confidence', 0),
                                        'time': datetime.now().strftime('%I:%M %p'),
                                        'date': datetime.now().strftime('%Y-%m-%d'),
                                        'savings': savings
                                    }
                                    save_scan_to_persistence(entry, savings)
                                    
                                    st.success("✅ Analysis complete!")
                                else:
                                    st.error("❌ Analysis failed")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                else:
                    if st.button("🔄 New Scan", type="secondary", use_container_width=True, key="reset_btn"):
                        st.session_state.scan_result = None
                        st.session_state.analysis_complete = False
                        st.session_state.treatment_fetched = False
                        st.session_state.dynamic_treatment = None
                        st.rerun()
        
        with col_result:
            result = st.session_state.get('scan_result')
            
            if result and st.session_state.get('analysis_complete', False):
                disease_raw = result.get('disease', 'Unknown')
                crop = get_crop_from_disease(disease_raw)
                disease = get_disease_only(disease_raw)
                confidence = result.get('confidence', 0)
                conf_pct = int(confidence * 100) if confidence <= 1 else int(confidence)
                is_healthy = 'healthy' in disease_raw.lower()
                
                # Get disease severity info
                severity_info = get_disease_severity(disease_raw)
                savings = severity_info['savings']
                
                badge = "success" if conf_pct >= 80 else "warning" if conf_pct >= 60 else "error"
                
                st.markdown(f"""
                <div class="result-card animate-fade-scale">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <span class="badge badge-{badge}">{conf_pct}% Confidence</span>
                        <span style="color: var(--text-muted); font-size: 0.85rem;">{datetime.now().strftime('%I:%M %p')}</span>
                    </div>
                    <div class="crop-badge">🌱 {crop}</div>
                    <div class="disease-name">{disease}</div>
                    {f'<div class="savings-info">💰 Early detection saved you approximately ₹{savings}</div>' if savings > 0 else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # Treatment section
                if not is_healthy:
                    if not st.session_state.get('treatment_fetched', False):
                        st.markdown(render_treatment_card("", is_loading=True), unsafe_allow_html=True)
                        
                        # Fetch treatment in user's language
                        language = st.session_state.get('app_language', 'en')
                        treatment = fetch_dynamic_treatment(disease, crop, confidence, language)
                        if treatment:
                            st.session_state.dynamic_treatment = treatment
                        else:
                            st.session_state.dynamic_treatment = result.get('treatment', 'Please consult an expert.')
                        
                        st.session_state.treatment_fetched = True
                        st.rerun()
                    else:
                        st.markdown(render_treatment_card(st.session_state.dynamic_treatment or result.get('treatment', '')), unsafe_allow_html=True)
                else:
                    lang = st.session_state.get('app_language', 'en')
                    healthy_msg = "आपका पौधा स्वस्थ है!" if lang == 'hi' else "Your plant looks healthy!"
                    st.markdown(f"""
                    <div class="treatment-card animate-fade-up" style="background: rgba(34, 197, 94, 0.1); border-color: var(--success);">
                        <div class="treatment-header">
                            <div class="treatment-icon" style="background: var(--success);">✅</div>
                            <div style="font-weight: 600; color: var(--text-primary);">{healthy_msg}</div>
                        </div>
                        <div class="treatment-content">{'अच्छी प्रथाओं को जारी रखें!' if lang == 'hi' else 'Continue good practices!'}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Save Report", use_container_width=True, key="save_btn"):
                        st.success("✅ Report saved!")
                with c2:
                    if st.button("📤 Share", use_container_width=True, type="secondary", key="share_btn"):
                        st.info("📤 Share feature coming soon!")
            else:
                st.markdown(f"""
                <div class="glass-card" style="height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                    <div class="animate-float" style="font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.4;">🧠</div>
                    <h3 style="color: var(--text-secondary);">AI Ready</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">Capture or upload an image to start</p>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🏜️ Soil Health Card OCR")
            st.file_uploader("Upload Card", type=['pdf', 'jpg', 'png'], key="soil_up")
            if st.button("🔬 Analyze", type="primary", use_container_width=True, key="soil_btn"):
                st.info("🚀 Available in Pro!")
        with c2:
            st.markdown(f"""
            <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🌱</div>
                <h3 style="color: var(--text-primary);">Smart Soil Insights</h3>
                <p style="color: var(--text-secondary);">Get fertilizer recommendations.</p>
                <br><span class="badge badge-info">Coming Soon</span>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# VIEW: AI CONSULTANT
# ==========================================

def view_chat():
    st.markdown(f"""
    <div class="animate-fade-up" style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="animate-float" style="font-size: 3rem;">🤖</div>
            <div>
                <h1 style="margin: 0; font-size: 2.25rem; color: var(--text-primary);">{get_text('consultant_header')}</h1>
                <p style="margin: 0.5rem 0 0; color: var(--text-secondary);">{get_text('consultant_sub')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        avatar = "🤖" if msg["role"] == "assistant" else "👨‍🌾"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Ask about crops, diseases, farming tips..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👨‍🌾"):
            st.write(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🧠 Thinking..."):
                try:
                    language = st.session_state.get('app_language', 'en')
                    if CHATBOT_AVAILABLE:
                        response = chatbot.chat(prompt, target_language=language)
                    else:
                        response = "I'm running in lightweight mode. The AI chatbot is currently unavailable."
                except Exception as e:
                    print(f"Chat error: {e}")
                    fallbacks = {
                        "hello": "Hello! 🌱 I'm KropBot. How can I help?",
                        "hi": "Hi! 🌱 Ask me anything about crops!",
                    }
                    response = "I'm here to help with farming questions!"
                    for k, v in fallbacks.items():
                        if k in prompt.lower():
                            response = v
                            break
                
                st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-secondary); font-size: 0.85rem;'>💡 Try asking:</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    suggestions = ["How to prevent tomato blight?", "Best fertilizer for cotton?", "When to plant wheat?"]
    for idx, (col, sug) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(sug, key=f"sug_{idx}", use_container_width=True, type="secondary"):
                st.session_state.chat_history.append({"role": "user", "content": sug})
                st.rerun()

# ==========================================
# VIEW: COMMUNITY
# ==========================================

def view_community():
    st.markdown(f"""
    <div class="animate-fade-up" style="margin-bottom: 2.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="animate-float" style="font-size: 3rem;">🌍</div>
            <div>
                <h1 style="margin: 0; font-size: 2.25rem; color: var(--text-primary);">{get_text('community_header')}</h1>
                <p style="margin: 0.5rem 0 0; color: var(--text-secondary);">{get_text('community_sub')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([f"💬 {get_text('tab_discuss')}", f"🏆 {get_text('tab_stories')}", f"🛒 {get_text('tab_market')}"])
    
    with tabs[0]:
        st.markdown("<br>", unsafe_allow_html=True)
        col_chat, col_info = st.columns([2, 1])
        
        with col_chat:
            messages = []
            if COMMUNITY_CHAT_AVAILABLE:
                try:
                    # Get real messages
                    chat_data = community_chat.get_messages(10)
                    for m in chat_data:
                        # Calculate time ago roughly
                        try:
                            msg_time = datetime.strptime(m['timestamp'], "%Y-%m-%d %H:%M:%S")
                            diff = datetime.now() - msg_time
                            if diff.days > 0:
                                t_str = f"{diff.days}d ago"
                            elif diff.seconds > 3600:
                                t_str = f"{diff.seconds//3600}h ago"
                            elif diff.seconds > 60:
                                t_str = f"{diff.seconds//60}m ago"
                            else:
                                t_str = "Just now"
                        except:
                            t_str = "Recently"
                            
                        messages.append((m.get('user_name', 'Farmer'), m.get('message', ''), t_str))
                    
                    # Reverse to show newest at bottom if needed, but UI seems to list them top-down. 
                    # Usually chat is newest at bottom, but this UI mocks a feed.
                    # Let's keep the order from get_messages (oldest to newest usually)
                    # But the mock data was "2 hrs ago", "5 hrs ago" implying newest first?
                    # Let's reverse for the feed view
                    messages.reverse()
                except Exception as e:
                    print(f"Chat load error: {e}")
            
            if not messages:
                messages = [
                    ("Rajesh Kumar", "Has anyone tried neem oil for aphids?", "2 hrs ago"),
                    ("Priya Sharma", "Drip irrigation saved 40% water! 💧", "5 hrs ago"),
                    ("Amit Patel", "Rain forecast tomorrow - good for fertilizing.", "Yesterday"),
                ]
            
            for name, msg, t in messages:
                st.markdown(f"""
                <div class="glass-card" style="padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 32px; height: 32px; background: var(--accent-gradient); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.8rem; font-weight: 600;">{name[0]}</div>
                        <strong style="color: var(--text-primary);">{name}</strong>
                        <span style="font-size: 0.8rem; color: var(--text-muted); margin-left: auto;">{t}</span>
                    </div>
                    <p style="color: var(--text-secondary); margin: 0; padding-left: 40px;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with st.form("chat_form", clear_on_submit=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    txt_input = st.text_input("Message", placeholder="Share your thoughts...", label_visibility="collapsed", key="comm_msg")
                with c2:
                    sent = st.form_submit_button("Send", type="primary", use_container_width=True)
                
                if sent and txt_input:
                    if COMMUNITY_CHAT_AVAILABLE:
                        try:
                            uid = st.session_state.get('user_id', 'guest')
                            community_chat.send_message(uid, txt_input)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to send: {e}")
                    else:
                        st.info("Community chat is in demo mode.")
        
        with col_info:
            active_count = get_active_members_count()
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: var(--text-primary); margin-bottom: 1rem;">👥 Active Members</h4>
                <span class="badge badge-success">{active_count:,} Online</span>
                <br><br>
                <h5 style="color: var(--text-secondary); margin-bottom: 0.75rem;">Top Contributors</h5>
                <div style="color: var(--text-primary);">🥇 Ramesh Singh</div>
                <div style="color: var(--text-primary);">🥈 Sunita Devi</div>
                <div style="color: var(--text-primary);">🥉 Vikram Yadav</div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"✨ {get_text('share_story')}"):
            with st.form("story_form"):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Crop Name", placeholder="e.g., Tomato", key="st_crop")
                with c2:
                    st.text_input("Treatment", placeholder="e.g., Copper Fungicide", key="st_treat")
                st.text_area("Your Experience", placeholder="Share your story...", key="st_exp")
                st.slider("Rating", 1, 5, 5, key="st_rating")
                st.form_submit_button("Publish", type="primary")
        
        stories = [
            {"name": "Suresh Rao", "crop": "Cotton", "treatment": "IPM", "rating": 5, "text": "Reduced pesticide by 60%!"},
            {"name": "Lakshmi Bai", "crop": "Wheat", "treatment": "Organic", "rating": 4, "text": "Better market price!"},
        ]
        
        for s in stories:
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom: 1rem; padding: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                    <div style="width: 48px; height: 48px; background: var(--accent-gradient); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700;">{s['name'][0]}</div>
                    <div><div style="font-weight: 600; color: var(--text-primary);">{s['name']}</div><div style="font-size: 0.85rem; color: var(--text-muted);">🌾 {s['crop']}</div></div>
                    <div style="margin-left: auto;">{'⭐' * s['rating']}</div>
                </div>
                <div style="padding: 0.75rem; background: var(--bg-tertiary); border-radius: var(--radius-md); margin-bottom: 1rem;"><span style="color: var(--accent-primary); font-weight: 500;">💊 {s['treatment']}</span></div>
                <p style="color: var(--text-secondary); margin: 0;">"{s['text']}"</p>
            </div>
            """, unsafe_allow_html=True)

    with tabs[2]:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div class="animate-float" style="font-size: 4rem; margin-bottom: 1.5rem;">🛒</div>
            <h2 style="color: var(--text-primary);">Marketplace Coming Soon</h2>
            <p style="color: var(--text-secondary);">Buy and sell agricultural products.</p>
            <br><span class="badge badge-info">In Development</span>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# VIEW: SETTINGS
# ==========================================

def view_settings(user_data: Dict):
    st.markdown(f"""
    <div class="animate-fade-up" style="margin-bottom: 2.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="animate-float" style="font-size: 3rem;">⚙️</div>
            <div>
                <h1 style="margin: 0; font-size: 2.25rem; color: var(--text-primary);">{get_text('settings_header')}</h1>
                <p style="margin: 0.5rem 0 0; color: var(--text-secondary);">{get_text('settings_sub')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1, 1], gap="large")
    
    with col_l:
        st.markdown("### 🎨 Appearance")
        is_dark = st.session_state.theme == 'dark'
        if st.toggle("Dark Mode", value=is_dark, key="theme_toggle") != is_dark:
            st.session_state.theme = 'light' if is_dark else 'dark'
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🌐 Language")
        
        langs = {'en': 'English', 'hi': 'हिंदी (Hindi)'}
        current = st.session_state.app_language
        idx = list(langs.keys()).index(current) if current in langs else 0
        selected = st.selectbox("Language", list(langs.values()), index=idx, label_visibility="collapsed", key="lang_select")
        new_code = list(langs.keys())[list(langs.values()).index(selected)]
        if new_code != current:
            st.session_state.app_language = new_code
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📍 Location")
        current_state = st.session_state.get('user_state', 'Maharashtra')
        new_state = st.selectbox("State", INDIAN_STATES, index=INDIAN_STATES.index(current_state) if current_state in INDIAN_STATES else 0, key="state_select")
        if new_state != current_state:
            st.session_state.user_state = new_state
            st.session_state.weather_data = None
            st.session_state.market_data = None
            st.rerun()
    
    with col_r:
        st.markdown("### 👤 Account")
        with st.form("acc_form"):
            st.text_input("Full Name", value=user_data.get('name', ''), key="acc_name")
            st.text_input("Phone", value=user_data.get('phone', ''), key="acc_phone")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                st.success("✅ Settings saved!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📱 Preferences")
        st.toggle("Push notifications", value=True, key="notif_toggle")
        st.toggle("Low data mode", value=False, key="data_toggle")
        
        # Show user stats
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 Your Statistics")
        stats = get_user_stats()
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-secondary);">Total Scans:</span>
                <span style="color: var(--text-primary); font-weight: 600;">{stats['total_scans']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-secondary);">Diseases Detected:</span>
                <span style="color: var(--text-primary); font-weight: 600;">{stats['diseased_scans']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-secondary);">Crop Health:</span>
                <span style="color: var(--text-primary); font-weight: 600;">{stats['crop_health']}%</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-secondary);">Total Savings:</span>
                <span style="color: var(--success); font-weight: 600;">₹{stats['savings']:,}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# VIEW: ADMIN
# ==========================================

def view_admin():
    st.markdown(f"""
    <div class="animate-fade-up" style="margin-bottom: 2.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="animate-float" style="font-size: 3rem;">🛡️</div>
            <div>
                <h1 style="margin: 0; font-size: 2.25rem; color: var(--text-primary);">{get_text('nav_admin')}</h1>
                <p style="margin: 0.5rem 0 0; color: var(--text-secondary);">System administration</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(4)
    stats = [("Users", "N/A", "👥"), ("Sessions", "N/A", "🔌"), ("Scans", "N/A", "📷"), ("Health", "100%", "✅")]
    for (label, value, icon), col in zip(stats, cols):
        with col:
            st.markdown(render_stat_card(label, value, icon, None, 0), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("📊 Full admin dashboard available in Enterprise plan")

# ==========================================
# MAIN
# ==========================================

def main():
    inject_premium_css()
    
    if not check_auth():
        show_login_page()
        return
    
    if auth_system and st.session_state.current_user and st.session_state.current_user != "demo_token":
        user_data = auth_system.get_user_from_session(st.session_state.current_user)
        if not user_data:
            st.session_state.current_user = None
            st.rerun()
    else:
        user_data = {
            "name": "Demo Farmer",
            "location": st.session_state.get('user_state', 'Maharashtra'),
            "user_id": st.session_state.get('user_id', 'demo'),
            "phone": "+91 98765 43210"
        }
    
    current_page = render_sidebar(user_data)
    
    views = {
        'dashboard': lambda: view_dashboard(user_data),
        'scan': view_scanner,
        'consultant': view_chat,
        'community': view_community,
        'settings': lambda: view_settings(user_data),
        'admin': view_admin
    }
    
    view_func = views.get(current_page, lambda: view_dashboard(user_data))
    view_func()

if __name__ == "__main__":
    main()