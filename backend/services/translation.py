from google.cloud import translate_v2 as translate
from config import settings

class TranslationService:
    def __init__(self):
        try:
            # Assumes GOOGLE_APPLICATION_CREDENTIALS is set in env
            self.translate_client = translate.Client()
            self.enabled = True
        except Exception as e:
            print(f"Google Cloud Translation not configured: {e}. Using mock/fallback.")
            self.enabled = False
            
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if target_lang == source_lang:
            return text
            
        if not self.enabled:
            return f"[Translated to {target_lang}]: {text}"
            
        try:
            result = self.translate_client.translate(
                text, target_language=target_lang, source_language=source_lang
            )
            return result['translatedText']
        except Exception as e:
            print(f"Translation error: {e}")
            return f"[Fallback translated to {target_lang}]: {text}"

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
