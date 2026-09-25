import os
import re

def replace_in_file(filepath, old, new):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

# 1. Models
replace_in_file("backend/models/diagnosis.py", "confidence: float", "model_confidence_score: float")
replace_in_file("backend/models/schema.py", "confidence = Column(Float", "model_confidence_score = Column(Float")

# 2. Services
with open("backend/services/gemini_service.py", "r") as f:
    g_content = f.read()
g_content = g_content.replace('"confidence": 0.0 to 1.0,', '"model_confidence_score": 0.0 to 1.0 (Note: this is a model-provided estimate, not a statistically calibrated probability),')
with open("backend/services/gemini_service.py", "w") as f:
    f.write(g_content)

replace_in_file("backend/services/persistence_service.py", "confidence=diagnosis_data.get(\"confidence\")", "model_confidence_score=diagnosis_data.get(\"model_confidence_score\")")
replace_in_file("backend/routers/diagnose.py", "\"confidence\": diagnosis_data.get(\"confidence\")", "\"model_confidence_score\": diagnosis_data.get(\"model_confidence_score\")")

# 3. Tests
replace_in_file("backend/tests/test_p01_regression.py", "\"confidence\":", "\"model_confidence_score\":")
replace_in_file("backend/tests/test_p03_outbreaks.py", "\"confidence\":", "\"model_confidence_score\":")

# 4. Frontend
replace_in_file("frontend/src/lib/types.ts", "confidence: number;", "model_confidence_score: number;")
replace_in_file("frontend/src/app/diagnose/page.tsx", "result.confidence < 75", "result.model_confidence_score < 0.75")
replace_in_file("frontend/src/app/diagnose/page.tsx", "getConfidenceLabel(result.confidence)", "getConfidenceLabel(result.model_confidence_score * 100)")
replace_in_file("frontend/src/app/diagnose/page.tsx", "result.confidence.toFixed(1)", "(result.model_confidence_score * 100).toFixed(1)")
replace_in_file("frontend/src/app/diagnose/page.tsx", "Confidence ({", "Model Estimate ({")
replace_in_file("frontend/src/lib/mock-data.ts", "confidence: 94.5", "model_confidence_score: 0.945")

