import logging
from google import genai
from google.genai import types
from config import settings

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.enabled = True
        except Exception as e:
            logger.error(f"Gemini client not configured for TranslationService: {e}. Using mock/fallback.")
            self.enabled = False
            
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if target_lang == source_lang:
            return text
            
        if not self.enabled:
            return f"[Translated to {target_lang}]: {text}"""
            
        language_map = {
            'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi', 'ta': 'Tamil', 
            'te': 'Telugu', 'bn': 'Bengali', 'kn': 'Kannada', 'gu': 'Gujarati', 
            'pa': 'Punjabi', 'ml': 'Malayalam'
        }
        
        full_source = language_map.get(source_lang, source_lang)
        full_target = language_map.get(target_lang, target_lang)
            
        try:
            prompt = f"""CRITICAL INSTRUCTION: You are a professional translator. Translate the following text from {full_source} to {full_target}. You MUST output ONLY the translated text in the native script of {full_target} and absolutely nothing else. Do not use romanized text unless the target is English.

Text:
{text}"""
            response = self.client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"[Fallback translated to {target_lang}]: {text}"""

    def get_supported_languages(self) -> list:
        return [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "mr", "name": "Marathi"},
            {"code": "ta", "name": "Tamil"},
            {"code": "te", "name": "Telugu"},
            {"code": "bn", "name": "Bengali"},
            {"code": "kn", "name": "Kannada"},
            {"code": "gu", "name": "Gujarati"},
            {"code": "pa", "name": "Punjabi"},
            {"code": "ml", "name": "Malayalam"}
        ]

translation_service = TranslationService()
