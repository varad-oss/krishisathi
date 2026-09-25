import re

with open("backend/models/diagnosis.py", "r") as f:
    diag = f.read()

header = """from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import base64
from enum import Enum
"""

diag = diag.replace("from typing import Optional, List\nfrom pydantic import BaseModel, Field\nfrom enum import Enum\n", header)

validator = """
    @field_validator('image')
    def validate_base64_image(cls, v):
        try:
            # Strip standard data URI header if present
            if v.startswith('data:'):
                v = v.split(',', 1)[1]
            decoded = base64.b64decode(v, validate=True)
            if len(decoded) > 5 * 1024 * 1024:
                raise ValueError('Decoded image size exceeds 5MB')
            return v
        except ValueError as e:
            if "exceeds" in str(e):
                raise
            raise ValueError('Invalid base64 encoding')
"""

diag = diag.replace("    language: str = 'en'\n", f"    language: str = 'en'\n{validator}\n")

with open("backend/models/diagnosis.py", "w") as f:
    f.write(diag)


with open("backend/models/advisory.py", "r") as f:
    adv = f.read()

adv_header = """from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import base64
"""

adv = adv.replace("from typing import Optional, List\nfrom pydantic import BaseModel, Field\n", adv_header)

adv_validator_img = """
    @field_validator('image_base64')
    def validate_image_base64(cls, v):
        if not v:
            return v
        try:
            if v.startswith('data:'):
                v = v.split(',', 1)[1]
            decoded = base64.b64decode(v, validate=True)
            if len(decoded) > 5 * 1024 * 1024:
                raise ValueError('Decoded image size exceeds 5MB')
            return v
        except ValueError as e:
            if "exceeds" in str(e):
                raise
            raise ValueError('Invalid base64 encoding')
"""
adv = adv.replace("    language: str = 'en'\n", f"    language: str = 'en'\n{adv_validator_img}\n", 1)

adv_validator_aud = """
    @field_validator('audio_base64')
    def validate_audio_base64(cls, v):
        try:
            if v.startswith('data:'):
                v = v.split(',', 1)[1]
            decoded = base64.b64decode(v, validate=True)
            if len(decoded) > 10 * 1024 * 1024:
                raise ValueError('Decoded audio size exceeds 10MB')
            return v
        except ValueError as e:
            if "exceeds" in str(e):
                raise
            raise ValueError('Invalid base64 encoding')
"""
adv = adv.replace("    language: str = 'hi'\n", f"    language: str = 'hi'\n{adv_validator_aud}\n")

with open("backend/models/advisory.py", "w") as f:
    f.write(adv)
