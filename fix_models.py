import re

# Update advisory models
with open("backend/models/advisory.py", "r") as f:
    content = f.read()

content = content.replace(
    "query: str = Field(..., min_length=1)",
    "query: str = Field(..., min_length=1, max_length=2000)"
).replace(
    "image_base64: Optional[str] = None",
    "image_base64: Optional[str] = Field(None, max_length=10_000_000)"
).replace(
    "audio_base64: str\n",
    "audio_base64: str = Field(..., max_length=10_000_000)\n"
)

with open("backend/models/advisory.py", "w") as f:
    f.write(content)

# Update diagnosis model
with open("backend/models/diagnosis.py", "r") as f:
    content = f.read()

content = content.replace(
    "image: str # base64 str",
    "image: str = Field(..., max_length=10_000_000) # base64 str"
)

with open("backend/models/diagnosis.py", "w") as f:
    f.write(content)
