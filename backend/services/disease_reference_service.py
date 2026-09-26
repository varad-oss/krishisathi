import json
import logging
import os

from services.crops import normalize_crop

logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "disease_reference.json")


class DiseaseReferenceService:
    def __init__(self):
        self.data = []
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f).get("diseases", [])
            logger.info("Loaded %d disease reference records.", len(self.data))
        except Exception as e:
            logger.error("Failed to load disease_reference.json: %s", e)

    def _crop_matches(self, crop_type: str | None) -> list[dict]:
        if not crop_type:
            return []
        wanted = {crop_type.lower()}
        canonical = normalize_crop(crop_type)
        if canonical:
            wanted.add(canonical.lower())
        return [item for item in self.data if wanted & {c.lower() for c in item.get("crops", [])}]

    def get(self, reference_id: str | None, crop_type: str | None = None) -> dict | None:
        """Returns a reference entry only if the id exists (and, when a crop is known, applies to it)."""
        if not reference_id:
            return None
        candidates = self._crop_matches(crop_type) if crop_type else self.data
        return next((item for item in candidates if item.get("id") == reference_id), None)

    def get_grounding_context(self, crop_type: str | None, state_code: str | None) -> str:
        if not crop_type:
            return ""
        crop_matches = self._crop_matches(crop_type)
        if not crop_matches:
            return "No specific regional disease reference data found for this context."

        final_matches, is_regional = crop_matches, False
        if state_code:
            state_matches = [m for m in crop_matches if state_code.upper() in m.get("states", [])]
            if state_matches:
                final_matches, is_regional = state_matches, True

        parts = []
        for m in final_matches:
            sources = "; ".join(f"{s.get('organization', '')} - {s.get('title', '')}" for s in m.get("sources", [])) or "Unknown Source"
            parts.append(
                f"- id: {m.get('id')}\n  Disease: {m.get('name', 'Unknown')}\n  Symptoms: {m.get('symptoms', '')}\n"
                f"  Treatment: {m.get('treatment', '')}\n  Source: {sources}"
            )
        header = "Regional Disease Reference Data:" if is_regional else "General Disease Reference Data:"
        return f"{header}\n" + "\n".join(parts)


disease_reference_service = DiseaseReferenceService()
