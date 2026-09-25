import re

with open("backend/models/interop.py", "r") as f:
    content = f.read()

content = content.replace(
    "message: str = Field(..., description=\"Human-readable signal description\")",
    "message: str = Field(..., description=\"Human-readable signal description\", max_length=1000)"
).replace(
    "disease_name: Optional[str] = None",
    "disease_name: Optional[str] = Field(None, max_length=200)"
).replace(
    "affected_crop: Optional[str] = None",
    "affected_crop: Optional[str] = Field(None, max_length=200)"
).replace(
    "affected_district: Optional[str] = None",
    "affected_district: Optional[str] = Field(None, max_length=200)"
)

with open("backend/models/interop.py", "w") as f:
    f.write(content)
