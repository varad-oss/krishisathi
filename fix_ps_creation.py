with open("backend/services/persistence_service.py", "r") as f:
    c = f.read()

c = c.replace('model_confidence_score=diagnosis_data.get("model_confidence_score"),\n                    aggregated_severity=aggregated_severity,', 'model_confidence_score=diagnosis_data.get("model_confidence_score"),\n                    model_inferred_severity=diagnosis_data.get("model_inferred_severity", "Medium"),')
c = c.replace('model_inferred_spread_risk=diagnosis_data.get("model_inferred_spread_risk", "Unknown")\n                )', 'model_inferred_spread_risk=diagnosis_data.get("model_inferred_spread_risk", "Unknown")\n                )')

with open("backend/services/persistence_service.py", "w") as f:
    f.write(c)
