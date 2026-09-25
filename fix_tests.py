import re

def replace_in_file(filepath, old, new):
    with open(filepath, 'r') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

replace_in_file("backend/tests/test_p03_outbreaks.py", 'severity="Medium"', 'model_inferred_severity="Medium"')
replace_in_file("backend/tests/test_p03_outbreaks.py", 'spread_risk="Medium"', 'model_inferred_spread_risk="Medium"')

# Let's also check test_p02_regression.py
replace_in_file("backend/tests/test_p02_regression.py", 'severity="Medium"', 'model_inferred_severity="Medium"')
replace_in_file("backend/tests/test_p02_regression.py", 'spread_risk="Medium"', 'model_inferred_spread_risk="Medium"')

