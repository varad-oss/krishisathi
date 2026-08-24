import json
from google import genai
from google.genai import types
from config import settings

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            print("WARNING: GEMINI_API_KEY not set. Using mock data.")

    def diagnose_crop_disease(self, image_bytes: bytes, crop_type: str, location_context: dict) -> dict:
        if not self.client:
            return self._get_mock_diagnosis(crop_type)
        
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
            
            prompt = f"""
            You are an expert agricultural plant pathologist. Analyze the provided image of a crop.
            Crop Type (if provided): {crop_type or 'Unknown'}
            Location Context: {location_context}
            
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
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.3,
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return self._get_mock_diagnosis(crop_type)

    def generate_advisory(self, query: str, context: dict) -> str:
        if not self.client:
            return "Based on mock data, ensure proper irrigation and apply balanced NPK fertilizers."
            
        try:
            prompt = f"""
            You are an expert agricultural advisor. Provide detailed, actionable advice for the following query.
            Query: {query}
            Context (Weather, soil, etc.): {context}
            
            Provide the advisory clearly and concisely.
            """
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.5,
                )
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return "Service temporarily unavailable. Ensure proper care of your crops based on local guidelines."
            
    def generate_dashboard_report(self, data: dict) -> str:
        if not self.client:
            return "This is a mock weekly report. No significant issues reported."
            
        try:
            prompt = f"""
            You are an agricultural data analyst. Generate a natural language weekly report from the following aggregated data for a policymaker dashboard.
            Data: {data}
            
            Keep the report professional, highlighting key insights, risks, and recommendations.
            """
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.4,
                )
            )
            return response.text
        except Exception as e:
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
