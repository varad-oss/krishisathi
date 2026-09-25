with open("backend/services/persistence_service.py", "r") as f:
    c = f.read()

c = c.replace('"severity": r.severity,', '"severity": r.aggregated_severity,')
c = c.replace('"severity": r.aggregated_severity,', '"severity": r.aggregated_severity,') # deduplicate just in case it was already replaced
with open("backend/services/persistence_service.py", "w") as f:
    f.write(c)
