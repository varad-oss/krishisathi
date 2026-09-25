with open("backend/routers/alerts.py", "r") as f:
    content = f.read()

import re
# Ensure we only process active outbreaks
content = content.replace("outbreaks = await persistence_service.get_outbreaks()", "outbreaks = [o for o in await persistence_service.get_outbreaks() if o['status'] == 'active']")

# Ensure /outbreaks returns active only
# Wait, replacing all of them handles all endpoints in alerts.py!

with open("backend/routers/alerts.py", "w") as f:
    f.write(content)

