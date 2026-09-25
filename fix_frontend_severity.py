import re

def replace_in_file(filepath, old, new):
    with open(filepath, 'r') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

replace_in_file("frontend/src/lib/types.ts", "severity: string;", "model_inferred_severity: string;")
replace_in_file("frontend/src/lib/types.ts", "spread_risk: string;", "model_inferred_spread_risk: string;")

replace_in_file("frontend/src/app/diagnose/page.tsx", "result.severity", "result.model_inferred_severity")
replace_in_file("frontend/src/app/diagnose/page.tsx", "result.spread_risk", "result.model_inferred_spread_risk")

replace_in_file("frontend/src/lib/mock-data.ts", "severity: \"Severe\",", "model_inferred_severity: \"Severe\",")
replace_in_file("frontend/src/lib/mock-data.ts", "spread_risk: \"High", "model_inferred_spread_risk: \"High")
