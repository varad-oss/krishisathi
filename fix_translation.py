import re

with open("backend/services/translation.py", "r") as f:
    py = f.read()

py = py.replace('prompt = f"CRITICAL INSTRUCTION:', 'prompt = f"""CRITICAL INSTRUCTION:')
py = py.replace('{text}"', '{text}"""')

with open("backend/services/translation.py", "w") as f:
    f.write(py)
