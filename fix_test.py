with open("backend/tests/test_p03_outbreaks.py", "r") as f:
    content = f.read()

import re
# Remove the sys.path from bottom
content = re.sub(r"import sys\nimport os\nsys\.path\.insert[\s\S]+?'\.\.'\)\)\n", "", content)

# Prepend it to the top
header = """import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""

with open("backend/tests/test_p03_outbreaks.py", "w") as f:
    f.write(header + content)

