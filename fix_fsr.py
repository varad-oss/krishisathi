with open("backend/services/persistence_service.py", "r") as f:
    c = f.read()

c = c.replace("aggregated_severity=signal.severity,", "severity=signal.severity,")
c = c.replace('"aggregated_severity": r.aggregated_severity,', '"severity": r.severity,')
c = c.replace("aggregated_severity=r.aggregated_severity,", "severity=r.severity,")

with open("backend/services/persistence_service.py", "w") as f:
    f.write(c)
