with open("frontend/src/lib/api.ts", "r") as f:
    c = f.read()

c = c.replace("severity: data.severity", "model_inferred_severity: data.model_inferred_severity")
c = c.replace("spread_risk: data.spread_risk || 'Unknown'", "model_inferred_spread_risk: data.model_inferred_spread_risk || 'Unknown'")
c = c.replace("data.confidence === 'number'", "data.model_confidence_score === 'number'")
c = c.replace("data.confidence <=", "data.model_confidence_score <=")
c = c.replace("data.confidence * 100", "data.model_confidence_score * 100")
c = c.replace("data.confidence,", "data.model_confidence_score,")

with open("frontend/src/lib/api.ts", "w") as f:
    f.write(c)

