import json
import logging
from google import genai
from google.genai import types
from config import settings
from services.disease_reference_service import disease_reference_service
from models.exceptions import ServiceUnavailableException

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.error("GEMINI_API_KEY not set. Gemini services will be unavailable.")

    def _call(self, prompt, image_part=None, model=None, response_mime_type=None, temperature=0.3, error_message="AI model is temporarily unavailable."):
        contents = [image_part, prompt] if image_part else [prompt]
        
        config = types.GenerateContentConfig(
            temperature=temperature,
        )
        if response_mime_type:
            config.response_mime_type = response_mime_type
            
        try:
            return self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except Exception as e:
            logger.error(f"{model} failed: {e}")
            raise ServiceUnavailableException(error_message) from e

    def diagnose_crop_disease(self, image_bytes: bytes, crop_type: str, location_context: dict) -> dict:
        if not self.client:
            raise ServiceUnavailableException("Diagnosis service is unavailable (API key missing).")
        
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
            
            state_code = location_context.get('state', '')
            grounding_context = disease_reference_service.get_grounding_context(crop_type, state_code)
            
            prompt = f"""
You are an expert agricultural plant pathologist. Analyze the provided image of a crop.

[OBSERVED FROM IMAGE]
Analyze the visual symptoms carefully.
Crop Type (if provided): {crop_type or 'Unknown'}

[REFERENCE KNOWLEDGE]
{grounding_context}

[ENVIRONMENTAL CONTEXT]
Location Context: {location_context}

INSTRUCTIONS:
1. Identify any disease or pest visible in the image.
2. Use the REFERENCE KNOWLEDGE strictly to compare symptoms and explain management. 
3. If the reference data contains no matching diseases, state the diagnosis based ONLY on the visual evidence, but DO NOT invent or hallucinate references.
4. DO NOT invent pesticide doses, concentrations, or regulatory claims. If a concrete chemical treatment is in the reference, you may state it, but always append: "Consult local agricultural authorities for exact dosage."

Return the response strictly as a JSON object with the following structure:
{{
    "disease_name": "Common name of the disease",
    "scientific_name": "Scientific name",
    "confidence": 0.0 to 1.0,
    "severity": "Low, Medium, or High",
    "affected_part": "Leaves, Stem, Roots, etc.",
    "treatment": {{
        "immediate": ["step 1", "step 2"],
        "organic": ["step 1"],
        "chemical": ["step 1", "Consult local agricultural authorities for exact dosage."],
        "prevention": ["step 1"]
    }},
    "spread_risk": "Low, Medium, or High",
    "image_analysis_summary": "Brief summary of what you see in the image",
    "advisory_text": "General advisory for the farmer"
}}
"""
            
            response = self._call(
                prompt=prompt, 
                image_part=image_part, 
                model=settings.GEMINI_DIAGNOSIS_MODEL,
                response_mime_type='application/json', 
                temperature=0.2,
                error_message="Diagnostic model is temporarily unavailable."
            )
            
            return json.loads(response.text)
        except ServiceUnavailableException:
            raise
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            raise ServiceUnavailableException("Diagnosis service failed to process the request.") from e

    def generate_advisory(self, query: str, context: dict, image_base64: str = None) -> str:
        if not self.client:
            raise ServiceUnavailableException("Advisory service is unavailable (API key missing).")
            
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
            
            response = self._call(
                prompt=prompt, 
                image_part=image_part,
                model=settings.GEMINI_ADVISORY_MODEL,
                temperature=0.5,
                error_message="Advisory model is temporarily unavailable."
            )
            return response.text
        except ServiceUnavailableException:
            raise
        except Exception as e:
            logger.error(f"Error calling Gemini for advisory: {e}")
            raise ServiceUnavailableException("Advisory service is temporarily unavailable.") from e
            
    def generate_dashboard_report(self, data: dict, language: str = 'en') -> str:
        if not self.client:
            raise ServiceUnavailableException("Reporting service is unavailable (API key missing).")
        try:
            lang_map = {'hi': 'Hindi', 'mr': 'Marathi', 'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali', 'kn': 'Kannada', 'gu': 'Gujarati', 'pa': 'Punjabi', 'ml': 'Malayalam', 'en': 'English'}
            lang_name = lang_map.get(language, 'English')
            
            prompt = f"""
            You are an agricultural data analyst. Generate a natural language weekly report from the following aggregated data for a policymaker dashboard.
            Data: {data}
            
            Keep the report professional, highlighting key insights, risks, and recommendations.
            CRITICAL INSTRUCTION: YOU MUST WRITE THE ENTIRE REPORT EXCLUSIVELY IN {lang_name} ({language}).
            """

            
            response = self._call(
                prompt=prompt, 
                model=settings.GEMINI_AGENT_MODEL,
                temperature=0.4,
                error_message="Reporting model is temporarily unavailable."
            )
            return response.text
        except ServiceUnavailableException:
            raise
        except Exception as e:
            logger.error(f"Error calling Gemini for report: {e}")
            raise ServiceUnavailableException("Reporting service is temporarily unavailable.") from e

gemini_service = GeminiService()
