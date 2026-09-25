with open("backend/routers/alerts.py", "r") as f:
    content = f.read()

import re
content = content.replace("if dist <= 150.0:", 'if dist <= outbreak["radius_km"] * 1.5:  # Add 50% margin for "nearby" alerts')
content = content.replace("High risk of {outbreak['disease']} detected", "{outbreak['severity']} risk of {outbreak['disease']} detected")

with open("backend/routers/alerts.py", "w") as f:
    f.write(content)

