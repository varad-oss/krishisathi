import re

# 1. models/diagnosis.py
with open("backend/models/diagnosis.py", "r") as f:
    c = f.read()
c = c.replace("severity: str", "model_inferred_severity: str")
c = c.replace("spread_risk: str", "model_inferred_spread_risk: str")
with open("backend/models/diagnosis.py", "w") as f:
    f.write(c)

# 2. gemini_service.py
with open("backend/services/gemini_service.py", "r") as f:
    c = f.read()
c = c.replace('"severity": "Low, Medium, or High",', '"model_inferred_severity": "Low, Medium, or High",')
c = c.replace('"spread_risk": "Low, Medium, or High",', '"model_inferred_spread_risk": "Low, Medium, or High",')
with open("backend/services/gemini_service.py", "w") as f:
    f.write(c)

# 3. routers/diagnose.py
with open("backend/routers/diagnose.py", "r") as f:
    c = f.read()
c = c.replace('diagnosis_data.get("severity")', 'diagnosis_data.get("model_inferred_severity")')
with open("backend/routers/diagnose.py", "w") as f:
    f.write(c)

# 4. persistence_service.py
with open("backend/services/persistence_service.py", "r") as f:
    c = f.read()
c = c.replace('severity=diagnosis_data.get("severity", "Medium")', 'model_inferred_severity=diagnosis_data.get("model_inferred_severity", "Medium")')
c = c.replace('spread_risk=diagnosis_data.get("spread_risk", "Unknown")', 'model_inferred_spread_risk=diagnosis_data.get("model_inferred_spread_risk", "Unknown")')

c = c.replace('severity=severity', 'aggregated_severity=aggregated_severity')
c = c.replace('existing_outbreak.severity', 'existing_outbreak.aggregated_severity')
c = c.replace('severity.lower()', 'aggregated_severity.lower()')
c = c.replace('severity = diagnosis_data.get("model_inferred_severity", "Medium")', 'aggregated_severity = diagnosis_data.get("model_inferred_severity", "Medium")')

c = c.replace('"severity": r.severity,', '"aggregated_severity": r.aggregated_severity,')
c = c.replace('severity=signal.severity,', 'aggregated_severity=signal.severity,')
c = c.replace('severity=r.severity,', 'aggregated_severity=r.aggregated_severity,')
c = c.replace('"severity": d.severity,', '"model_inferred_severity": d.model_inferred_severity,')
with open("backend/services/persistence_service.py", "w") as f:
    f.write(c)
