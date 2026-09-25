with open("backend/services/persistence_service.py", "r") as f:
    c = f.read()

c = c.replace('severity = diagnosis_data.get("severity", "Medium")', 'aggregated_severity = diagnosis_data.get("model_inferred_severity", "Medium")')
c = c.replace('existing_outbreak.aggregated_aggregated_severity', 'existing_outbreak.aggregated_severity')
c = c.replace('aggregated_severity=signal.severity', 'aggregated_severity=signal.severity') # signal still uses severity probably? wait, let's check interop.py

with open("backend/services/persistence_service.py", "w") as f:
    f.write(c)
