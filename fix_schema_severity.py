with open("backend/models/schema.py", "r") as f:
    content = f.read()

content = content.replace("severity = Column(String, nullable=False)", "model_inferred_severity = Column(String, nullable=False)", 1)
content = content.replace("spread_risk = Column(String, nullable=False)", "model_inferred_spread_risk = Column(String, nullable=False)", 1)

content = content.replace("severity = Column(String, nullable=False)", "aggregated_severity = Column(String, nullable=False)", 1)

with open("backend/models/schema.py", "w") as f:
    f.write(content)
