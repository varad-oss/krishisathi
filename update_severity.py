import os

def replace_in_file(filepath, old, new):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

# Models
replace_in_file("backend/models/diagnosis.py", "severity: str", "model_inferred_severity: str")
replace_in_file("backend/models/diagnosis.py", "spread_risk: str", "model_inferred_spread_risk: str")
replace_in_file("backend/models/schema.py", "severity = Column(String(50))", "model_inferred_severity = Column(String(50))")
# Wait, for OutbreakRecord, I'll keep it as severity for now, or change to aggregated_severity.
# Let's just do it manually.
