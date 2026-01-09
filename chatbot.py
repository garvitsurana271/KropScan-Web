# chatbot.py
try:
    from groq import Groq
    import httpx
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Groq not available, using fallback response system")

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("Deep Translator not available")
except Exception as e:
    TRANSLATOR_AVAILABLE = False
    print(f"Deep Translator not available: {e}")

class KropBot:
    def __init__(self):
        if GROQ_AVAILABLE:
            # Your API key
            try:
                self.client = Groq(api_key="grok_key")
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
                self.client = None
        else:
            self.client = None

        self.system_prompt = """You are KropBot, an agricultural expert helping Indian farmers.

Rules:
- Give SHORT answers (2-3 sentences max)
- Use simple words
- Focus on practical solutions
- If farmer asks in Hindi, reply in Hindi
- Always be encouraging

Examples:
Farmer: "My tomato leaves have brown spots"
You: "This looks like Early Blight fungus. Spray Mancozeb fungicide (available at any agri shop for ₹200). Remove the infected leaves and burn them."

Farmer: "Meri fasal mein keede lag gaye"
You: "Neem ka spray use karein (1 liter pani mein 5ml Neem oil). Subah ya shaam ko spray karein, dopahar mein nahi."
"""

    def chat(self, user_message, target_language='en'):
        if GROQ_AVAILABLE and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",  # ← UPDATED MODEL
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                response_text = response.choices[0].message.content

                # Translate response if target language is not English
                if target_language != 'en' and TRANSLATOR_AVAILABLE:
                    try:
                        translated_response = GoogleTranslator(source='en', target=target_language).translate(response_text)
                        return translated_response
                    except Exception as e:
                        print(f"Translation error: {e}")
                        return response_text  # Return original if translation fails
                else:
                    return response_text
            except Exception as e:
                # If Groq fails, use fallback
                print(f"Groq error: {e}")
                return self.get_fallback_response(user_message, target_language)
        else:
            # Use fallback response system
            return self.get_fallback_response(user_message, target_language)

    def get_fallback_response(self, message, target_language='en'):
        """Provide a fallback response when Groq is not available"""
        message_lower = message.lower()

        # Define some basic responses for common agricultural questions
        if any(word in message_lower for word in ["hello", "hi", "hey", "namaste"]):
            response = "Hello! I'm your KropBot agricultural assistant. How can I help you with your farming questions today?"

        elif any(word in message_lower for word in ["disease", "diseased", "sick", "infected"]):
            response = "For crop diseases, I recommend taking a clear photo of the affected plant parts for accurate diagnosis. You can use the 'Scan Crop' feature to identify diseases and get treatment recommendations."

        elif any(word in message_lower for word in ["treatment", "cure", "remedy", "heal"]):
            response = "Treatment depends on the specific disease. After using the 'Scan Crop' feature, you'll receive detailed treatment recommendations based on the identified disease."

        elif any(word in message_lower for word in ["fertilizer", "manure", "nutrient", "feed"]):
            response = "For fertilization, consider using balanced NPK fertilizers. Organic options like compost and vermicompost are also excellent for soil health. The specific needs depend on your crop type and soil conditions."

        elif any(word in message_lower for word in ["water", "irrigation", "watering"]):
            response = "Proper irrigation is crucial. Water deeply but less frequently to encourage deep root growth. Drip irrigation is the most efficient method. Avoid overhead watering to prevent disease spread."

        elif any(word in message_lower for word in ["weather", "rain", "temperature", "climate"]):
            response = "Weather greatly affects crop health. Monitor local weather forecasts to plan irrigation, pesticide applications, and harvesting. Consider weather-resistant crop varieties for your region."

        elif any(word in message_lower for word in ["pest", "insect", "bug", "worm"]):
            response = "For pest management, consider integrated pest management (IPM) practices: use beneficial insects, pheromone traps, neem-based pesticides, and crop rotation. Identify the specific pest for targeted treatment."

        else:
            response = f"I received your message: '{message}'. For the best agricultural advice, I recommend using our 'Scan Crop' feature to diagnose plant issues or asking specific questions about farming practices. I'm here to help with crop care, disease prevention, and agricultural best practices."

        # Translate response if target language is not English
        if target_language != 'en' and TRANSLATOR_AVAILABLE:
            try:
                translated_response = GoogleTranslator(source='en', target=target_language).translate(response)
                return translated_response
            except Exception as e:
                print(f"Translation error: {e}")
                return response  # Return original if translation fails
        else:
            return response

# Test if it works
if __name__ == "__main__":
    bot = KropBot()
    print(bot.chat("How do I treat tomato blight?"))
