with open("backend/tests/test_p03_outbreaks.py", "r") as f:
    c = f.read()

c = c.replace('"severity":', '"model_inferred_severity":')
with open("backend/tests/test_p03_outbreaks.py", "w") as f:
    f.write(c)
