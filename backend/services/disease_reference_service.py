import json
import os
import logging

logger = logging.getLogger(__name__)

class DiseaseReferenceService:
    def __init__(self):
        self.data = []
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'disease_reference.json')
            if not os.path.exists(data_path):
                # Fallback just in case
                data_path = os.path.join(os.getcwd(), 'backend', 'data', 'disease_reference.json')
                
            with open(data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f).get('diseases', [])
            logger.info(f"Loaded {len(self.data)} disease reference records.")
        except Exception as e:
            logger.error(f"Failed to load disease_reference.json: {e}")

    def get_grounding_context(self, crop_type: str, state_code: str) -> str:
        if not crop_type:
            return ""
            
        crop_matches = []
        for item in self.data:
            crops = [c.lower() for c in item.get('crops', [])]
            if crop_type.lower() in crops:
                crop_matches.append(item)
                
        if not crop_matches:
            return "No specific regional disease reference data found for this context."
            
        # Try state matching if provided
        final_matches = []
        is_regional = False
        
        if state_code:
            state_matches = [m for m in crop_matches if state_code.upper() in m.get('states', [])]
            if state_matches:
                final_matches = state_matches
                is_regional = True
                
        if not final_matches:
            final_matches = crop_matches
            
        context_parts = []
        for m in final_matches:
            disease = m.get('name', 'Unknown')
            symptoms = m.get('symptoms', '')
            treatment = m.get('treatment', '')
            
            # Format sources
            sources = m.get('sources', [])
            source_texts = []
            for s in sources:
                org = s.get('organization', '')
                title = s.get('title', '')
                source_texts.append(f"{org} - {title}")
            source_str = "; ".join(source_texts) if source_texts else "Unknown Source"
            
            context_parts.append(f"- Disease: {disease}\n  Symptoms: {symptoms}\n  Treatment: {treatment}\n  Source: {source_str}")
            
        header = "Regional Disease Reference Data:" if is_regional else "General Disease Reference Data:"
        return f"{header}\n" + "\n".join(context_parts)

disease_reference_service = DiseaseReferenceService()
