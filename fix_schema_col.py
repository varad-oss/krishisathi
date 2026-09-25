with open("backend/models/schema.py", "r") as f:
    c = f.read()

c = c.replace("model_inferred_aggregated_severity = Column", "model_inferred_severity = Column")

with open("backend/models/schema.py", "w") as f:
    f.write(c)
