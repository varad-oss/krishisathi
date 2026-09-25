with open("backend/services/persistence_service.py", "r") as f:
    c = f.read()

c = c.replace('spread_risk=diagnosis_data.get("spread_risk", "Medium")', 'model_inferred_spread_risk=diagnosis_data.get("model_inferred_spread_risk", "Medium")')

with open("backend/services/persistence_service.py", "w") as f:
    f.write(c)
