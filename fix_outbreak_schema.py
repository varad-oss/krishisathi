with open("backend/models/schema.py", "r") as f:
    c = f.read()

c = c.replace('    severity = Column(String, nullable=False)\n    report_count = Column', '    aggregated_severity = Column(String, nullable=False)\n    report_count = Column')

with open("backend/models/schema.py", "w") as f:
    f.write(c)
