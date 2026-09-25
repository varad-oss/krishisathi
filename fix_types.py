import re

with open("frontend/src/lib/types.ts", "r") as f:
    c = f.read()

c = re.sub(r"severity: 'Low' \| 'Moderate' \| 'Severe' \| 'Critical';", r"model_inferred_severity: 'Low' | 'Medium' | 'High' | 'Severe' | 'Critical';", c, count=1)

with open("frontend/src/lib/types.ts", "w") as f:
    f.write(c)

with open("frontend/src/lib/api.ts", "r") as f:
    a = f.read()
a = a.replace("confidence:", "model_confidence_score:")
with open("frontend/src/lib/api.ts", "w") as f:
    f.write(a)

