from typing import Dict, List, Optional
import json

class LanguageService:
    """
    Service to handle multilingual support for the application.
    """

    def __init__(self):
        # Define supported languages
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi',
            'te': 'Telugu',
            'ta': 'Tamil',
            'kn': 'Kannada',
            'ml': 'Malayalam'
        }

        self.translator = None
        self.translator_available = False

        # Attempt to load Deep Translator, handling specific library conflicts
        try:
            from deep_translator import GoogleTranslator
            self.translator_available = True
        except (ImportError, Exception) as e:
            print(f"Translation service warning: {e}. Falling back to static translations.")
            self.translator_available = False

        # Define fallback translations (Expanded)
        self.base_terms = {
            # Navigation
            'nav_dashboard': 'Dashboard',
            'nav_scan': 'Smart Scan',
            'nav_consultant': 'AI Consultant',
            'nav_community': 'Community Hub',
            'nav_settings': 'Settings',
            'nav_admin': 'System Admin',
            'nav_logout': 'Logout',
            
            # Dashboard
            'welcome': 'Good morning',
            'farm_overview': 'Here is your farm status',
            'metric_health': 'Crop Health',
            'metric_scans': 'Active Scans',
            'metric_savings': 'Savings',
            'metric_weather': 'Weather',
            'quick_actions': 'Quick Actions',
            'btn_scan': 'Start New Scan',
            'btn_consultant': 'Ask Assistant',
            'btn_calendar': 'View Calendar',
            'recent_analysis': 'Recent Analysis',
            'mandi_prices': 'Real-Time Mandi Prices',
            
            # Scanner
            'scan_header': 'Smart Diagnostics',
            'scan_sub': 'Advanced AI-powered disease detection system.',
            'acquire_image': '1. Acquire Image',
            'source_upload': 'Upload File',
            'source_camera': 'Camera',
            'run_analysis': 'Run Analysis',
            'soil_health': 'Soil Health (OCR)',
            'soil_desc': 'Upload Soil Health Card',
            'analyze_soil': 'Analyze Soil Card',
            
            # Consultant
            'consultant_header': 'AI Consultant',
            'consultant_sub': 'Your expert agronomist, available 24/7.',
            
            # Community
            'community_header': 'Community Hub',
            'community_sub': 'Connect with fellow farmers.',
            'tab_discuss': 'Discussion Board',
            'tab_stories': 'Success Stories',
            'tab_market': 'Marketplace',
            'share_story': 'Share Your Success Story',
            'story_crop': 'Crop Name',
            'story_treatment': 'Treatment Used',
            'story_review': 'Your Experience',
            'story_submit': 'Publish Story',
            
            # Settings
            'settings_header': 'Settings',
            'settings_sub': 'Customize your experience.',
            'appearance': 'Appearance',
            'language': 'Language',
            'account': 'Account',
            'offline_mode': 'Offline Mode (PWA)',
            'voice_nav': 'Voice Navigation',
            
            # Common
            'loading': 'Loading...',
            'success': 'Success',
            'error': 'Error',
            'save': 'Save'
        }
        
        # We will populate other languages dynamically or partially here to avoid massive file size
        # Ideally, these should be loaded from a JSON file.
        self.fallback_translations = {
            'hi': {
                'nav_dashboard': 'डैशबोर्ड', 'nav_scan': 'स्मार्ट स्कैन', 'nav_consultant': 'AI सलाहकार',
                'welcome': 'नमस्ते', 'metric_health': 'फसल स्वास्थ्य', 'mandi_prices': 'मंडी भाव',
                'btn_scan': 'नया स्कैन', 'run_analysis': 'विश्लेषण करें'
            },
            'mr': {
                'nav_dashboard': 'डॅशबोर्ड', 'nav_scan': 'स्मार्ट स्कॅन', 'nav_consultant': 'AI सल्लागार',
                'welcome': 'नमस्कार', 'metric_health': 'पीक आरोग्य', 'mandi_prices': 'बाजार भाव',
                'btn_scan': 'नवीन स्कॅन', 'run_analysis': 'विश्लेषण करा'
            }
        }
    
    def translate(self, text_key: str, target_lang: str = 'en', **kwargs) -> str:
        """
        Translate a text key to the target language.
        Prioritizes:
        1. Static fallback dictionary (fastest, reliable)
        2. Google Translate (if available and not in fallback)
        3. English base term
        """
        
        # Get English base
        base_text = self.base_terms.get(text_key, text_key)
        
        # 1. Check Static Fallback
        if target_lang in self.fallback_translations:
            if text_key in self.fallback_translations[target_lang]:
                return self.fallback_translations[target_lang][text_key].format(**kwargs)

        # 2. Dynamic Translate (if working)
        if self.translator_available and target_lang != 'en':
            try:
                # We translate the *value* of the base term, not the key
                from deep_translator import GoogleTranslator
                result = GoogleTranslator(source='en', target=target_lang).translate(base_text)
                return result
            except Exception:
                # Silently fail back to English to prevent app crash
                pass

        # 3. Return English/Base
        try:
            return base_text.format(**kwargs)
        except:
            return base_text

    def get_supported_languages(self) -> Dict[str, str]:
        return self.supported_languages
