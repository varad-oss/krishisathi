import json
import os
import logging

logger = logging.getLogger(__name__)

class DiseaseReferenceService:
    def __init__(self):
        self.data = []
        try:
            # Assuming backend is running in backend/ and data is in ../data
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'disease_reference.json')
            if not os.path.exists(data_path):
                # Try relative to cwd
                data_path = os.path.join(os.getcwd(), '..', 'data', 'disease_reference.json')
                
            with open(data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f).get('diseases', [])
            logger.info(f"Loaded {len(self.data)} disease reference records.")
        except Exception as e:
            logger.error(f"Failed to load disease_reference.json: {e}")

    def get_grounding_context(self, crop_type: str, state_code: str) -> str:
        if not crop_type:
            return ""
            
        matches = []
        for item in self.data:
            crops = [c.lower() for c in item.get('crops', [])]
            if crop_type.lower() in crops:
                matches.append(item)
                
        if not matches:
            return "No specific regional disease reference data found for this context."
            
        context_parts = []
        for m in matches:
            disease = m.get('name', 'Unknown')
            symptoms = m.get('symptoms', '')
            treatment = m.get('treatment', '')
            context_parts.append(f"- Disease: {disease}\n  Symptoms: {symptoms}\n  Treatment: {treatment}")
            
        return "Regional Disease Reference Data:\n" + "\n".join(context_parts)

disease_reference_service = DiseaseReferenceService()
