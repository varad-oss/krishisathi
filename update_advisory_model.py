import re

with open("backend/models/advisory.py", "r") as f:
    py = f.read()

py = py.replace('crop_type: Optional[str] = None', 'crop_type: Optional[str] = None\n    image_base64: Optional[str] = None')

with open("backend/models/advisory.py", "w") as f:
    f.write(py)
