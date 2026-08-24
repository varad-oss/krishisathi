import json
import logging
from google import genai
from google.genai import types
from config import settings
from services.disease_reference_service import disease_reference_service

logger = logging.getLogger(__name__)

MODEL_FLASH = 'gemini-flash-lite-latest'
MODEL_PRO = 'gemini-flash-lite-latest'

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY not set. Using mock data.")

    def _call_with_fallback(self, prompt, image_part=None, use_pro=True, response_mime_type=None, temperature=0.3):
        contents = [image_part, prompt] if image_part else [prompt]
        
        config = types.GenerateContentConfig(
            temperature=temperature,
        )
        if response_mime_type:
            config.response_mime_type = response_mime_type
            
        model = MODEL_PRO if use_pro else MODEL_FLASH
        
        try:
            return self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except Exception as e:
            import traceback; traceback.print_exc()
            logger.warning(f"{model} failed ({e}), falling back to {MODEL_FLASH}")
            if use_pro:
                return self.client.models.generate_content(
                    model=MODEL_FLASH,
                    contents=contents,
                    config=config
                )
            raise e

    def diagnose_crop_disease(self, image_bytes: bytes, crop_type: str, location_context: dict) -> dict:
        if not self.client:
            return self._get_mock_diagnosis(crop_type)
        
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
            
            # Fetch RAG Grounding context
            state_code = location_context.get('state', '')
            grounding_context = disease_reference_service.get_grounding_context(crop_type, state_code)
            
            prompt = f"""
            You are an expert agricultural plant pathologist. Analyze the provided image of a crop.
            Crop Type (if provided): {crop_type or 'Unknown'}
            Location Context: {location_context}
            
            Reference Grounding Data for regional diseases:
            {grounding_context}
            
            Identify any disease or pest visible in the image. Return the response strictly as a JSON object with the following structure:
            {{
                "disease_name": "Common name of the disease",
                "scientific_name": "Scientific name",
                "confidence": 0.0 to 1.0,
                "severity": "Low, Medium, or High",
                "affected_part": "Leaves, Stem, Roots, etc.",
                "treatment": {{
                    "immediate": ["step 1", "step 2"],
                    "organic": ["step 1"],
                    "chemical": ["step 1"],
                    "prevention": ["step 1"]
                }},
                "spread_risk": "Low, Medium, or High",
                "image_analysis_summary": "Brief summary of what you see in the image",
                "advisory_text": "General advisory for the farmer"
            }}
            """
            
            response = self._call_with_fallback(
                prompt=prompt, 
                image_part=image_part, 
                use_pro=True, 
                response_mime_type='application/json', 
                temperature=0.3
            )
            
            return json.loads(response.text)
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"Error calling Gemini: {e}")
            return self._get_mock_diagnosis(crop_type)

    def generate_advisory(self, query: str, context: dict, image_base64: str = None) -> str:
        if not self.client:
            return "Based on mock data, ensure proper irrigation and apply balanced NPK fertilizers."
            
        try:
            prompt = f"""
            You are an expert agricultural advisor. Provide detailed, actionable advice for the following query.
            Query: {query}
            Context (Weather, soil, etc.): {context}
            
            Provide the advisory clearly and concisely.
            """
            
            image_part = None
            if image_base64:
                import base64
                from google.genai import types
                img_bytes = base64.b64decode(image_base64)
                image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            
            response = self._call_with_fallback(
                prompt=prompt, 
                image_part=image_part,
                use_pro=False, 
                temperature=0.5
            )
            return response.text
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"Error calling Gemini: {e}")
            return "Service temporarily unavailable. Ensure proper care of your crops based on local guidelines."
            
    def generate_dashboard_report(self, data: dict, language: str = 'en') -> str:
        if not self.client:
            return "This is a mock weekly report. No significant issues reported."
        try:
            lang_map = {'hi': 'Hindi', 'mr': 'Marathi', 'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali', 'kn': 'Kannada', 'gu': 'Gujarati', 'pa': 'Punjabi', 'ml': 'Malayalam', 'en': 'English'}
            lang_name = lang_map.get(language, 'English')
            
            prompt = f"""
            You are an agricultural data analyst. Generate a natural language weekly report from the following aggregated data for a policymaker dashboard.
            Data: {data}
            
            Keep the report professional, highlighting key insights, risks, and recommendations.
            CRITICAL INSTRUCTION: YOU MUST WRITE THE ENTIRE REPORT EXCLUSIVELY IN {lang_name} ({language}).
            """

            
            response = self._call_with_fallback(
                prompt=prompt, 
                use_pro=True, 
                temperature=0.4
            )
            return response.text
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"Error calling Gemini: {e}")
            return "Error generating report."

    def _get_mock_diagnosis(self, crop_type: str) -> dict:
        return {
            "disease_name": "Leaf Blight (Mock)",
            "scientific_name": "Alternaria spp.",
            "confidence": 0.85,
            "severity": "Medium",
            "affected_part": "Leaves",
            "treatment": {
                "immediate": ["Remove infected leaves"],
                "organic": ["Apply neem oil extract"],
                "chemical": ["Apply appropriate fungicide"],
                "prevention": ["Ensure proper spacing for air circulation"]
            },
            "spread_risk": "Medium",
            "image_analysis_summary": "Dark brown spots with concentric rings observed on the leaves.",
            "advisory_text": "Monitor the crop closely and apply treatments immediately to prevent spread."
        }

gemini_service = GeminiService()
